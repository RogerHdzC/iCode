from django.db import models
from django.db.models.query import QuerySet
from django.db.models import Max
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView, FormView
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect
from django.forms import inlineformset_factory

from student.forms import CodingExerciseSolveForm, MultipleChoiceExerciseSolveForm, CodingReviewFormSet, MultipleChoiceReviewFormSet
from core.models import Exercise, Assignment, ExerciseInstanceInAssignment, ExerciseTestCase, ExerciseChoice, Submission
from core.judge0 import test_code
from members.models import CustomUser
from .models import Course, Enrollment
from .forms import MultipleChoiceExerciseForm, CodingExerciseForm, AssignmentForm, AssignmentExerciseGroupFormSet, ExerciseTestCaseFormSet, ExerciseChoiceFormSet, MultipleExercisesForm, ExerciseTestCaseForm, ExerciseChoiceForm

import requests
import json
import re

from time import sleep
from typing import Any, Dict, Optional
from unidecode import unidecode
from traceback import format_exc
from datetime import datetime


class CourseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Muestra a un profesor una lista de todos los cursos en los que este es administrador (los que hayan sido creados por este profesor).
    '''
    model = Course
    #template_name = 'professor/course_list.html'

    def get_queryset(self):
        qs = super().get_queryset() 
        return qs.filter(created_by=self.request.user)

    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class CourseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''Permite a un profesor crear un nuevo curso al que se pueden inscribir los estudiantes.
    '''
    model = Course
    fields = ['name']
    success_url = reverse_lazy('professor:courses')

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class ExerciseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Muestra los ejercicios creados por este profesor en una tabla que muestra el título del ejercicio, estado de aceptación y mensaje del administrador.
    '''
    model = Exercise
    template_name = 'professor/exercise_list.html'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(created_by=self.request.user)
        
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class MultipleChoiceExerciseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''Permite a un profesor crear un nuevo ejercicio de opción múltiple desde una interfaz gráfica o cargándolo desde un JSON.
    '''
    model = Exercise
    success_url = reverse_lazy('professor:new_multiple_choice')
    form_class = MultipleChoiceExerciseForm
    template_name = 'core/multiplechoiceexercise_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('formset'):
            context['formset'] = ExerciseChoiceFormSet()
        return context

    def form_valid(self, form, formset):
        form.instance.exercise_type = 1
        form.instance.created_by = self.request.user      
        self.object = form.save()
        
        options = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
            
        for option in options:
            option.exercise = self.object
            option.save()
            
        return super().form_valid(form)
        
    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )
        
    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ExerciseChoiceFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)
    
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR
        

class MultipleChoiceExerciseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Permite a un profesor actualizar un nuevo ejercicio de opción múltiple desde una interfaz gráfica o cargándolo desde un JSON.
    '''
    model = Exercise
    success_url = reverse_lazy('professor:my_exercises')
    form_class = MultipleChoiceExerciseForm
    template_name = 'core/multiplechoiceexercise_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = ExerciseChoiceFormSet(instance=self.object)
        return context

    def form_valid(self, form, formset):
        form.instance.status = self.object.IN_REVIEW
        self.object = form.save()
        
        options = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
            
        for option in options:
            option.exercise = self.object
            option.save()
            
        return super().form_valid(form)
        
    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ExerciseChoiceFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR
    
    
class CodingExerciseCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''Permite a un profesor crear un nuevo ejercicio de codificación desde una interfaz gráfica o cargándolo desde un JSON.
    '''
    model = Exercise
    success_url = reverse_lazy('professor:new_coding')
    form_class = CodingExerciseForm
    template_name = 'core/codingexercise_form.html'
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('formset'):
            context['formset'] = ExerciseTestCaseFormSet()
        return context

    def form_valid(self, form, formset):
        form.instance.created_by = self.request.user      
        self.object = form.save()
        
        test_cases = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()

        for test_case in test_cases:
            test_case.exercise = self.object
            test_case.save()
            
        return super().form_valid(form)
        
    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = ExerciseTestCaseFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)
            
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class CodingExerciseUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    '''Permite a un profesor actualizar un nuevo ejercicio de codificación desde una interfaz gráfica o cargándolo desde un JSON.
    '''
    model = Exercise
    success_url = reverse_lazy('professor:my_exercises')
    form_class = CodingExerciseForm
    template_name = 'core/codingexercise_form.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['formset'] = ExerciseTestCaseFormSet(instance=self.object)
        return context

    def form_valid(self, form, formset):
        form.instance.status = self.object.IN_REVIEW
        self.object = form.save()
        
        test_cases = formset.save(commit=False)
        for obj in formset.deleted_objects:
            obj.delete()
        for test_case in test_cases:
            test_case.exercise = self.object
            test_case.save()
            
        return super().form_valid(form)
        
    def form_invalid(self, form, formset):
        return self.render_to_response(
            self.get_context_data(form=form, formset=formset)
        )

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = ExerciseTestCaseFormSet(request.POST, instance=self.object)
        if form.is_valid() and formset.is_valid():
            return self.form_valid(form, formset)
        else:
            return self.form_invalid(form, formset)

    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class AddMultipleExercisesView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    '''Permite agregar múltiples ejercicios al mismo tiempo desde archivos JSON. 
    '''
    form_class = MultipleExercisesForm
    template_name = 'core/add_multiple_exercises.html'
    success_url = reverse_lazy('professor:add_multiple_exercises')
    
    def post(self, request):
        upload_results = []
        multi_form = MultipleExercisesForm(request.POST, request.FILES)
        for file in request.FILES.getlist('exercise_files'):
            try:
                data = json.load(file)
                
                # Muchos de los ejercicios originales tenían variaciones en la manera en que se referían a la dificultad media (intermedia, mediana, etc), por lo que las siguientes líneas de código estandarizan su escritura.  
                data['difficulty'] = unidecode(data.get('difficulty', 'media').lower())
                if 'media' in data['difficulty']:
                    data['difficulty'] = 'media'
                    
                # Identifica el tema por su número para evitar problemas por errores ortográficos.
                try:
                    data['topic'] = re.search(r'[0-9]+\.[0-9]+', data['topic']).group(0)
                except:
                    raise Exception('No se encontró el número del tema en el json.')
                    
                # identifica el tipo de ejercicio dependiendo si el JSON contiene el atributo 'tests' u 'options'
                if data.get('tests'):
                    form = CodingExerciseForm(data)
                    test_cases = data.get('tests')
                    for test_case in test_cases:
                        test_case['test_input'] = test_case.pop('input')
                        test_case['expected_output'] = test_case.pop('output')
                    exercise_child_forms = [ExerciseTestCaseForm(test_case) for test_case in test_cases]
                elif data.get('options'):
                    form = MultipleChoiceExerciseForm(data)
                    options = data.get('options')
                    exercise_child_forms = [ExerciseChoiceForm(option) for option in options]
                else:
                    raise Exception('El json no contiene todos los atributos de un ejercicio de código u opción múltiple.')
                
                if form.is_valid() and all([f.is_valid() for f in exercise_child_forms]):
                    exercise = form.save(commit=False)
                    exercise.created_by = self.request.user
                    if data.get('options'):
                        exercise.exercise_type = exercise.CHOICE
                    exercise.save()
                    
                    exercise_child_elements = [f.save(commit=False) for f in exercise_child_forms]
                    for element in exercise_child_elements:
                        element.exercise = exercise
                        element.save()
                    upload_results.append((str(file), True, ''))
                else:
                    f_errors = [f.errors for f in exercise_child_forms]
                    child_form_errors = ''.join([str(f.errors) for f in exercise_child_forms])
                    raise Exception(f'{form.errors}{child_form_errors}')
                    
            except Exception as e:
                upload_results.append((str(file), False, e))
                
        return render(request, self.template_name, context={'upload_results': upload_results, 'form': self.get_form()}) 
    
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class ExerciseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Permite a un profesor eliminar ejercicios que este haya creado.
    '''
    model = Exercise
    success_url = reverse_lazy('professor:my_exercises')
    
    def test_func(self):
        exercise = self.get_object()
        return exercise.created_by == self.request.user


class CourseDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Permite a un profesor eliminar un curso que este haya creado.
    '''
    model= Course
    success_url = reverse_lazy('professor:courses')

    def test_func(self):
        course = self.get_object()
        return course.created_by == self.request.user


class CourseStudentsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Muestra al profesor una lista de los estudiantes inscritos en este curso. También muestra los botones para eliminar el curso o eliminar a un estudiante del curso y un botón para copiar el id del curso y poder compartirlo con los estudiantes.
    '''
    model = Course
    template_name = 'professor/course_students.html'

    def test_func(self):
        course = self.get_object()
        return course.created_by == self.request.user
        
        
class CourseAssignmentsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Muestra una lista de todas las actividades del curso y la fecha límite de cada una de estas.
    '''
    model = Course
    template_name = 'professor/course_assignments.html'

    def test_func(self):
        course = self.get_object()
        return course.created_by == self.request.user


class EnrollmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Permite a un profesor eliminar a un estudiante de un curso que este haya creado.
    '''
    model = Enrollment

    def get_success_url(self):
        course_id = self.kwargs['course_id']
        return reverse_lazy('professor:course_students', kwargs={'pk': course_id})
        
    def get_object(self):
        course_id = self.kwargs.get('course_id')
        student_id = self.kwargs.get('student_id')
        enrollment = get_object_or_404(Enrollment, course__id=course_id, student__id=student_id)
        return enrollment

    def test_func(self):
        enrollment = self.get_object()
        return enrollment.course.created_by == self.request.user


class AssignmentCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    '''Permite a un profesor crear nuevas actividades para un curso determinado. Se sobreescribe la función form_valid para guardar los objetos de tipo AssignmentExerciseGroup, ya que estos son guardados en su propia tabla en la base de datos.
    '''
    model = Assignment
    form_class = AssignmentForm
        
    def get_initial(self):
        initial = self.initial.copy() 
        initial['due'] = datetime.now().replace(hour=23, minute=59, second=0).strftime('%Y-%m-%dT%H:%M')
        return initial
    
    def get_success_url(self):
        course_id = self.kwargs['course_id']
        return reverse_lazy('professor:course_assignments', kwargs={'pk': course_id})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if not context.get('exercise_formset'):
            context['exercise_formset'] = AssignmentExerciseGroupFormSet()
        context['course_id'] = self.kwargs['course_id']
        return context

    def form_valid(self, form, exercise_formset):
        course = Course.objects.get(id=self.kwargs['course_id'])
        form.instance.course = course
        
        self.object = form.save()
        assignment_exercises = exercise_formset.save(commit=False)

        for exercise_group in assignment_exercises:
            exercise_group.assignment = self.object
            exercise_group.save()
            
        return super().form_valid(form)

    def form_invalid(self, form, exercise_formset):
        return self.render_to_response(
            self.get_context_data(form=form, exercise_formset=exercise_formset)
        )

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        exercise_formset = AssignmentExerciseGroupFormSet(request.POST)

        if form.is_valid() and exercise_formset.is_valid():
            return self.form_valid(form, exercise_formset)
        else:
            return self.form_invalid(form, exercise_formset)
            
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class AssignmentSubmissionsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Muestra las entregas de estudiantes para una actividad particular de un curso.
    '''
    model = Assignment
    template_name = 'professor/assignment_submissions.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        student_list = []
        for student in self.object.course.students.all():
            submitted = Submission.objects.filter(student=student, assignment=self.object).exists()
            grade = Submission.objects.filter(student=student, assignment=self.object).aggregate(Max('grade')).get('grade__max')
            student_list.append((student, submitted, grade))
        context['student_list'] = student_list
        
        return context
    
    def test_func(self):
        return self.request.user.role == self.request.user.PROFESSOR


class SubmissionDetailView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Muestra los detalles de una entrega de un actividad por un estudiante.
    '''
    model = Submission
    template_name = 'professor/submission_detail.html'
    allow_empty = False
    
    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        student_id = self.kwargs.get('student_id')
        queryset = Submission.objects.filter(assignment__id=assignment_id, student__id=student_id)
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        submission_list = []
        for n, submission in enumerate(self.object_list):
            multiple_choice_exercises = ExerciseInstanceInAssignment.objects.filter(submission=submission.id, exercise__exercise_type=1)
            coding_exercises = ExerciseInstanceInAssignment.objects.filter(submission=submission.id, exercise__exercise_type=0)
            
            multiple_choice_formset = None
            coding_formset = None
            
            if multiple_choice_exercises:
                multiple_choice_formset = MultipleChoiceReviewFormSet(queryset=multiple_choice_exercises, prefix=f'multiplechoice_{n}')
                
            if coding_exercises:
                coding_formset = CodingReviewFormSet(queryset=coding_exercises, prefix=f'coding_{n}')
                
            submission_list.append((submission, multiple_choice_formset, coding_formset))
            
        context['submission_list'] = submission_list
        return context
        
    def test_func(self):
        assignment_id = self.kwargs.get('assignment_id')
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        return self.request.user == assignment.course.created_by
    

class AssignmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    '''Permite a un profesor eliminar una actividad de un curso.
    '''
    model = Assignment
    
    def get_success_url(self):
        course_id = self.object.course.id
        return reverse_lazy('professor:course_assignments', kwargs={'pk': course_id})

    def test_func(self):
        assignment = self.get_object()
        return assignment.course.created_by == self.request.user


# Se recomienda refactorizar esta vista utilizando 'CodingExerciseSolveForm' y 'MultipleChoiceExerciseSolveForm' de la applicación student para que el código sea más natural y fácil de comprender.
class ReviewExercise(LoginRequiredMixin, DetailView):
    '''Permite la revisión de ejercicios de código y opción múltiple en la página de admin.
    '''
    template_name = 'professor/review_exercise.html'
    model = Exercise

    def checkCodingAnswer(self, exercise, code):
        test_cases = exercise.test_cases.all()
        test_results = test_code(code, test_cases)
            
        return test_results

    def checkMultipleAnswer(self, exercise, user_answer):
        options = []
        options.append(str(exercise.answer) == user_answer)
        options.append(str(exercise.options.all()[(exercise.answer)-1].text))
        options.append(str(exercise.options.all()[int(user_answer)-1].text))
        options.append(str(exercise.explanation))
        return options

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        id = self.object.id
        form = CodingExerciseSolveForm(request.POST)
        m_form = None
        test_cases = []
        options = []
        exercise = Exercise.objects.get(id=id)
        test_results = []

        if exercise.exercise_type == 0:
            solution = request.POST['solution']
            test_results = self.checkCodingAnswer(exercise, solution)
            tests_passed = test_results['tests_passed']
            stdout_list = test_results['stdout_list']
            expected_output_list = test_results['expected_output_list']
            input_list = test_results['input_list']
            test_results = zip(input_list, expected_output_list, stdout_list, tests_passed)
        elif exercise.exercise_type == 1:
            solution = request.POST.get(str(id) + '-solution')
            if not solution:
                solution = request.POST['solution']
            choices = [(str(index+1), option.text) for index, option in enumerate(exercise.options.all())]
            m_form = MultipleChoiceExerciseSolveForm()
            correct_ans, ex_ans, selected_ans, explanation = self.checkMultipleAnswer(exercise, solution)
            options = {'correct_ans':correct_ans, 'ex_ans':ex_ans, 'selected_ans':selected_ans, 'explanation':explanation}

        ctx = {'checked':True, 'test_results': test_results, 
               'exercise': exercise, 'coding_form':form, 'options':options, 'm_form':m_form}
        return render(request, self.template_name, ctx)

    def get_context_data(self, **kwargs):
        context =  super().get_context_data(**kwargs)
        pk = self.kwargs['pk']
        exercise = Exercise.objects.get(id=pk)
        
        multiple_choice_forms = []
        assignment_display = []

        if exercise.exercise_type == 0:
            assignment_display.append((exercise, 'Coding'))
        elif exercise.exercise_type == 1:
            assignment_display.append((exercise, 'Multiple'))
            choices = [(str(index+1), option.text) for index, option in enumerate(exercise.options.all())]
            form = MultipleChoiceExerciseSolveForm(prefix=f"{exercise.id}")
            multiple_choice_forms.append(form)
            

        context['multiple_choice_forms'] = multiple_choice_forms
        context['coding_form'] = CodingExerciseSolveForm()
        context['exercises'] = assignment_display
        context['title'] = exercise.title

        return context
    



