from django.utils import timezone
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.utils.text import slugify
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.decorators import login_required
from django.db.models import Max
from asgiref.sync import async_to_sync, sync_to_async

from professor.models import Course, Enrollment
from core.models import Assignment, CompletedLevelsPerUser, Exercise, AssignmentExerciseGroup, ExerciseInstanceInAssignment, Subject, Submission, ExerciseTestCase
from .forms import CourseJoinForm, CodingSolveFormSet, MultipleChoiceSolveFormSet, CodingReviewFormSet, MultipleChoiceReviewFormSet
from core.judge0 import test_code, run_code

import collections
import uuid
import traceback
import json
import random
import requests
import time
import asyncio

from typing import Any, Dict, Optional
from time import sleep
from graphviz import Digraph
from unidecode import unidecode


class CourseListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Esta vista sirve para mostrarle a un estudiante los cursos en los que está inscrito. Incluye un campo de entrada de texto mediante "CourseJoinForm()" que permite al estudiante inscribirse a un curso ingresando el id del curso
    '''
    model = Course
    template_name = 'student/course_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CourseJoinForm()
        return context

    def get_queryset(self):
        return self.request.user.courses.all()

    def test_func(self):
        return self.request.user.role == self.request.user.STUDENT


class CourseAssignmentsView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Muestra una lista de todas las asignaciones del curso y la fecha límite de cada una de estas.
    '''
    model = Course
    template_name = 'student/course_assignments.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        assignments = Assignment.objects.filter(course=self.object)
        
        assignment_list = []
        for assignment in assignments:
            available = timezone.now() < assignment.due  
            pending_submission = Submission.objects.filter(student=self.request.user, assignment=assignment, delivered=False).exists()
            
            previous_submissions = Submission.objects.filter(student=self.request.user, assignment=assignment, delivered=True)
            submitted_attempts = previous_submissions.count()
            current_grade = previous_submissions.aggregate(Max('grade')).get('grade__max')
            assignment_list.append((assignment, available, pending_submission, submitted_attempts, current_grade))
            
        context['assignment_list'] = assignment_list
        return context
    
    def test_func(self):
        return Enrollment.objects.filter(course=self.kwargs.get('pk'), student=self.request.user).exists()


def format_test_cases(test_cases):
    '''Función que regresa los casos de prueba de un ejercicio como una lista de tuplas en las que el primer elemento es el input y el segundo es el output esperado. Esta función es necesaria porque la función test_code es asíncrona para mejorar el rendimiento de la ejecución del código y un QuerySet (resultado de una consulta de la base de datos con el ORM de Django) no funciona correctamente desde un contexto asíncrono, por lo tanto se utiliza esta función para pasar la información de los casos de prueba en un formato compatible.
    '''
    return [(test_case.test_input, test_case.expected_output) for test_case in test_cases]
    
def format_coding_exercises(exercise_instances):
    '''Función que regresa una lista de tuplas en la que el primer elemento de una tupla es el código ingresado por el usuario para resolver el ejercicio y el segundo elemento es una lista de los casos de prueba del ejercicio. Existe por la misma razón que la función format_test_cases.
    '''
    result = []
    for instance in exercise_instances:
        result.append((instance.solution, format_test_cases(instance.exercise.test_cases.all())))
    return result

class SubmissionCreateView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    '''Permite a un estudiante entregar una actividad correspondiente a un curso en el que esté inscrito.
    '''
    model = Submission
    template_name = 'student/assignment_solve.html'
        
    def check_multiple_choice_exercises(self, exercises):
        '''Método que recibe una lista de ejercicios de opción múltiple y compara la opción seleccionada por el usuario con la opción correcta del ejercicio. Regresa los puntos correspondientes a los ejercicios correctos para que este valor sea utilizado en el cálculo de la calificación de la actividad.
        '''
        points = 0.0
        for exercise_instance in exercises:            
            if int(exercise_instance.solution) == int(exercise_instance.exercise.answer):
                exercise_instance.passed = True
                points += 1.0
            exercise_instance.save()
        return points

    async def check_coding_exercises(self, exercises):
        '''Método que recibe una lista de ejercicios de codificación en el formato utilizado por la función format_coding_exercises y compara el resultado real con el esperado por cada uno de los casos de prueba del ejercicio. Regresa una lista con la puntuación de cada ejercicio proporcional a los casos de prueba que pasaron en relación al número total de casos de prueba del ejercicio. La lista de puntajes mantiene el orden en que se evaluaron los ejercicios. 
        '''
        exercise_scores = []
        actions = []
        for code, test_cases in exercises:
            actions.append(asyncio.ensure_future(test_code(code, test_cases)))
            
        test_results = await asyncio.gather(*actions)
        for i, result in enumerate(test_results):
            tests_passed = result['tests_passed']
            exercise_scores.append(sum(1 for t in tests_passed if t) / len(tests_passed))
 
        return exercise_scores

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        multiple_choice_formset = MultipleChoiceSolveFormSet(request.POST, prefix='multiplechoice', queryset=ExerciseInstanceInAssignment.objects.filter(submission=self.object, exercise__exercise_type=1))
        coding_formset = CodingSolveFormSet(request.POST, prefix='coding', queryset=ExerciseInstanceInAssignment.objects.filter(submission=self.object, exercise__exercise_type=0))
        
        if multiple_choice_formset.is_valid() and coding_formset.is_valid():
            return self.form_valid(multiple_choice_formset, coding_formset)
        else:
            return self.form_invalid(multiple_choice_formset, coding_formset)
        
    def form_valid(self, multiple_choice_formset, coding_formset):
        # ~ start = time.time()
        multiple_choice_exercises = multiple_choice_formset.save(commit=False)
        coding_exercises = coding_formset.save(commit=False)

        formatted_coding_exercises = format_coding_exercises(coding_exercises)
        
        points = 0.0
        points += self.check_multiple_choice_exercises(multiple_choice_exercises)
        
        coding_exercise_scores = async_to_sync(self.check_coding_exercises)(formatted_coding_exercises)
        for i, score in enumerate(coding_exercise_scores):
            if score == 1:
                coding_exercises[i].passed = True
            points += score
            coding_exercises[i].save()
        
        submission = self.object
        submission.delivered = True
        submission.grade = points / (len(coding_exercises) + len(multiple_choice_exercises)) * 100
        submission.submit_time = timezone.now()
        submission.save()
        messages.success(self.request, ("Actividad entregada!"))
        # ~ print('time to submit assignment = ' + str(time.time()-start))
        
        return redirect('student:course_assignments', pk=self.object.assignment.course.id)

    def form_invalid(self, multiple_choice_formset, coding_formset):
        return self.render_to_response(
            self.get_context_data(multiple_choice_formset=multiple_choice_formset, coding_formset=coding_formset)
        )
    
    def get_object(self, queryset=None):
        '''En caso de que haya un intento pendiente de la actividad regresa ese intento, de lo contrario crea un nuevo intento y sus ejercicios correspondientes y regresa el nuevo intento.
        '''
        assignment_id = self.kwargs.get('assignment_id')
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        student = self.request.user
        
        submission = None
        try:
            submission = Submission.objects.get(assignment=assignment, student=student, delivered=False)
        except Exception:
            submission = Submission(assignment=assignment, student=student, start_time=timezone.now())
            submission.save()
                
        return submission
        
    def create_submission_exercise_instances(self):
        '''Función que se encarga de crear las instancias de ejercicios correspondientes a esta entrega.
        '''
        assignment_id = self.kwargs['assignment_id']
        exercise_groups = AssignmentExerciseGroup.objects.filter(assignment=assignment_id)
        submission_exercises = []
        
        for exercise_group in exercise_groups:
            topic = exercise_group.topic
            difficulty = exercise_group.difficulty
            exercise_type = exercise_group.exercise_type
            count = exercise_group.count
            r = Exercise.objects.filter(topic=topic, difficulty=difficulty, exercise_type=exercise_type, status=2)
            submission_exercises += random.sample(list(r), count)
                    
        for exercise in submission_exercises:
            ExerciseInstanceInAssignment.objects.create(exercise=exercise, submission=self.object, solution="", passed=False)

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        if not self.object.exercise_instances.exists():
            self.create_submission_exercise_instances()
        
        if not context.get('multiple_choice_formset') and not context.get('coding_formset'):
            submission = self.object
            exercise_instances = submission.exercise_instances.all()

            multiple_choice_exercises = ExerciseInstanceInAssignment.objects.filter(submission=submission.id, exercise__exercise_type=1)
            coding_exercises = ExerciseInstanceInAssignment.objects.filter(submission=submission.id, exercise__exercise_type=0)
            
            multiple_choice_formset = MultipleChoiceSolveFormSet(queryset=multiple_choice_exercises, prefix='multiplechoice')
            context['multiple_choice_formset'] = multiple_choice_formset
                
            coding_formset = CodingSolveFormSet(queryset=coding_exercises, prefix='coding')
            context['coding_formset'] = coding_formset
                    
        context['duration'] = self.object.assignment.duration.total_seconds()
        return context
        
    def test_func(self):
        assignment_id = self.kwargs['assignment_id']
        assignment = get_object_or_404(Assignment, pk=assignment_id)
        due = assignment.due
        now = timezone.now()
        user = self.request.user

        return all([
            Enrollment.objects.filter(course=assignment.course, student=user).exists(),
            now < due,
            Submission.objects.filter(assignment=assignment, student=user, delivered=True).count() < assignment.attempts
        ])
        

class ReviewSubmissionView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    '''Permite a un estudiante revisar sus entregas de una actividad.
    '''
    model = Submission
    template_name = 'student/review_submission.html'
    allow_empty = False
    
    def get_queryset(self):
        assignment_id = self.kwargs.get('assignment_id')
        student_id = self.request.user.id
        queryset = Submission.objects.filter(assignment__id=assignment_id, student__id=student_id, delivered=True)
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
        
    def test_func(self): # verificar si se necesitan restricciones adicionales para prevenir que un estudiante pueda ver entregas de otros estudiantes.
        return self.request.user.role == self.request.user.STUDENT


@login_required
def join_course(request):
    '''Vista utilizada para manejar la inscripción de un estudiante a un curso. Busca un curso con un id igual al ingresado por el estudiante. En caso de encontrarlo, agrega al estudiante a la lista de estudiantes inscritos en el curso. De lo contrario, redirige a la página anterior con un mensaje de error.
    '''
    user = request.user
    if user.role == user.STUDENT and request.method == 'POST':
        form = CourseJoinForm(request.POST)
        if form.is_valid():
            try:
                course_id = form.cleaned_data['course_id']
                course_uuid = uuid.UUID(course_id)
                course = Course.objects.get(id=course_uuid)
                course.students.add(request.user)
            except:
                messages.error(request, "No se encontró el curso.")
    return redirect('student:courses')
    

@csrf_exempt
def test_code_view(request):
    '''Función que se encarga de probar el código del usuario en una actividad recibido mediante una solicitud ajax y regresa una respuesta json con los resultados de probar todos los casos de prueba del ejercicio correspondiente.
    '''
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        # ~ start = time.time()
        code = request.POST.get('solution')
        instance_id = request.POST.get('instance_id')
        exercise_instance = ExerciseInstanceInAssignment.objects.get(id=instance_id)
        exercise_instance.solution = code
        exercise_instance.save()
        
        test_cases = exercise_instance.exercise.test_cases.all()
        test_cases = format_test_cases(test_cases)
        
        sync_test_code = async_to_sync(test_code)
        test_results = sync_test_code(code, test_cases)

        response_data = {
            'success': True,
            'message': 'Ejecucion exitosa',
            'stdout_list': test_results['stdout_list'],
            'input_list': test_results['input_list'],
            'expected_output_list': test_results['expected_output_list'],
            'tests_passed': test_results['tests_passed'],
        }

        # ~ print('time to complete = ' + str(time.time()-start))
        
        return JsonResponse(response_data)

    return JsonResponse({'success': True, 'message': 'No es una solicitud Ajax'})


@csrf_exempt
def time_out(request):
    '''Función para terminar un intento de una actividad en caso de que se acabe el tiempo disponible para este. (Se requiere actualizar esta función) 
    '''
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        messages.warning(request, "Tiempo Agotado")
        redirect_url = reverse('student:courses')
        return JsonResponse({'redirect_url': redirect_url})
    
    return JsonResponse({'success': False})
