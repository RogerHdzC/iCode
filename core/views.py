from django.shortcuts import get_object_or_404, render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView
from django.http import HttpResponse
from django.urls import reverse_lazy
from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse
from django.db.models import Count, Subquery
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin

from core.forms import CodingExerciseInputForm, CodeInputForm
from .models import Subject, SubjectRelation, CompletedLevelsPerUser, ExerciseInstanceInGeneralPath, Exercise
from core.judge0 import test_code, run_code

import sys
import ast
import random
import requests
import json
from pyparsing import Any
from unidecode import unidecode
from graphviz import Digraph
from time import sleep
from io import StringIO

class HomeView(LoginRequiredMixin, FormView):
    '''
    Esta es la vista que se encarga de controlar el uso de código por parte del usuario. Estamos utilizando el servicio de Judge0, montando en una maquina virtual
    con el cual nosotros nos encargamos de poder tener llamadas a la API de este servicio con el código del usuario, obtener un Token único, y poder posteriormente 
    desplegar el resultado de ese código en pantalla.

    Decidimos utilizar Judge0 por las facilidades que da en cuestiones de seguridad que otras funciones como Exec, asi como la libertad que da el poder tenerlo montado
    en un servidor propio.

    Ademas, se encarga de procesar los test-cases de los ejercicios de codigo de la ruta general, se encarga de comprobar input y output y otorgar
    el resultado correspondiente al codigo del usuario. Esto es util ya que nosotros controlamos los inputs y outputs del codigo.
    '''
    template_name = 'core/home.html'
    form_class = CodeInputForm
    success_url = reverse_lazy('home')

    def post(self, request):
        form = CodeInputForm(request.POST)

        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        code = form.cleaned_data['code_input']
        code = unidecode(code)

        res = run_code(code)
        ctx = {'form': form, 'result': res['stdout']}

        return render(request, self.template_name, ctx)
    

class GraphView(LoginRequiredMixin, TemplateView):
    '''
    Vista utilizada para poder desplegar en el template main_path.html la ruta general de aprendizaje mostrada en su relacion de nodos.
    Aquí se tiene en cuenta los objetos del modelo SubjectRelation para poder, haciendo uso de la libreria Digraph, crear los nodos del grafo,
    darles un estilo y darles funcionalidad tambien. Cada uno al interactuar con el te envia a su propia pagina donde se deberan resolver 
    sus ejercicios correspondientes.
    '''
    template_name = 'core/main_path.html'

    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)

        relations = SubjectRelation.objects.all()
        graph = Digraph()

        user_completed_levels = CompletedLevelsPerUser.objects.filter(user=self.request.user, level = "Completado")
        completed_subjects = [str(completed_level.subject) for completed_level in user_completed_levels]

        graph.node_attr.update({'shape': 'Mrecord', 'peripheries': '2', 'fixedsize': 'true', 'width': '0.5', 'height': '0.5'})
        graph.attr('node', fontsize='11', width='2.48', height='0.75', fontname='Trebuchet MS')
        
        for relation in relations:
            first_char = relation.source.name[0]
            first_char_d = relation.destination.name[0]

            # Establecer el color de fondo del nodo según el primer caracter
            if first_char == '1':
                fill_color = '#6495ED'
            elif first_char == '2':
                fill_color = '#8FBC8F'
            elif first_char == '3':
                fill_color = "#CFC868"
            elif first_char == '4':
                fill_color = '#FFB6C1'
            elif first_char == '5':
                fill_color = '#000080'
            elif first_char == '6':
                fill_color = '#BA55D3'
            else:
                fill_color = '#FF3333'  # Color predeterminado para otros casos
            
            # Crear el nodo y establecer atributos
            tmp = relation.source.name
            source_name = relation.source.name
            if len(source_name.split()) > 4:
                source_name = " ".join(source_name.split(None, 4)[:4]) + '\n' + " ".join(source_name.split(None, 4)[4:])
            
            dest_name = relation.destination.name
            if len(dest_name.split()) > 4:
                dest_name = " ".join(dest_name.split(None, 4)[:4]) + '\n' + " ".join(dest_name.split(None, 4)[4:])


            if '1.1' in source_name:
                 graph.node(source_name, href=reverse('core:subject', args=[relation.source.pk]),
                    style='filled', fillcolor=fill_color, fontcolor='white')
                 
            if tmp in completed_subjects:
                graph.node(dest_name, href=reverse('core:subject', args=[relation.destination.pk]),
                        style='filled', fillcolor=fill_color, fontcolor='white')
            else:
                graph.node(dest_name, style='filled', fillcolor='gray', fontcolor='white')

            
            graph.edge(source_name, dest_name)
            
                        
        graph.edge_attr.update(arrowhead='normal', arrowsize='0.5') 
        svg = graph.pipe(format='svg').decode('utf-8')

        context['svg'] = svg
        return context
    
    def test_func(self):
        return self.request.user.role == self.request.user.STUDENT
    

#CHECAR SKIPS

@csrf_exempt
def actualizar_skips(request):
    '''
    Funcion que se encarga de recibir las llamadas desde el template de los ejercicios de la Ruta General y que 
    administra el numero de skips que tiene el usuario actualmente y les añade uno hasta llegar a un maximo de 3 niveles
    por dificultad y por tema.
    '''

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        
        data = json.loads(request.body)
        skips = data['skips']
        level = data['level']
        subject = data['subject']

        topic = Subject.objects.filter(id = subject)

        user = request.user
        try:
            obj = CompletedLevelsPerUser.objects.get(user = user, level = level, subject=subject)
            print(obj.skips)
            obj.skips += 1
            obj.save()
            return JsonResponse({'success':True})
        except CompletedLevelsPerUser.DoesNotExist:
            return JsonResponse({'success':False, 'message':'El usuario no existe'})
    
    return JsonResponse({'success': False, 'message':'No es solicitud Ajax'})




class SubjectDetailView(LoginRequiredMixin, DetailView):
    '''Muestra los ejercicios correspondientes al tema seleccionado por el alumno, de igual manera
    determina el nivel actual del usuario y se encarga de filtrar los ejercicios en base a ese nivel y
    que al mismo tiempo sean ejercicios nuevos para el usuario
    '''


    model = Subject
    form_class = CodingExerciseInputForm
    template_name = 'core/subject_detail.html'
    code = ""

    def levelUp(self, request):
        pk = self.kwargs['pk']

        topic = get_object_or_404(Subject, pk=pk)

        current_level = CompletedLevelsPerUser.objects.filter(subject=topic, user=self.request.user).first()

        l = ""
        if not current_level:
            l = "Facil"
        else:
            l = current_level.level

        passed_exercises = ExerciseInstanceInGeneralPath.objects.filter(user=self.request.user, 
                                                                        exercise__topic = topic, 
                                                                        exercise__difficulty = l, passed=True).count()
        print(passed_exercises)
        if current_level:
            
            if passed_exercises > 5 and current_level.level == "facil":
                    print("ya entre facil")
                    CompletedLevelsPerUser.objects.filter(user = self.request.user, subject = topic).update(level="media", skips=0)
                    return "Intermedio"
            elif passed_exercises > 5 and current_level.level == "media":
                    CompletedLevelsPerUser.objects.filter(user = self.request.user, subject = topic).update(level="dificil", skips=0)
                    return "Dificil"
            elif passed_exercises > 5 and current_level.level == "dificil":
                    CompletedLevelsPerUser.objects.filter(user = self.request.user,subject = topic).update(level = "Completado", skips=0)
                    return "Completado"
    
        

        
    def post(self, request, *args, **kwargs):
        form = CodingExerciseInputForm(request.POST)
        if not form.is_valid():
            ctx = {'form': form}
            return render(request, self.template_name, ctx)
        
        code = form.cleaned_data['solution']
        selected_exercise_id = request.session.get('selected_exercise_id')
        if selected_exercise_id:
            selected_exercise = Exercise.objects.get(id=selected_exercise_id)
        else:
            selected_exercise = None
        
        test_cases = selected_exercise.test_cases
        
        test_results = test_code(code, test_cases)
        tests_passed = test_results['tests_passed']
        stdout_list = test_results['stdout_list']

        failed_exercises = ExerciseInstanceInGeneralPath.objects.filter(user=self.request.user, 
                                                                        exercise__topic = selected_exercise.topic, 
                                                                        exercise__difficulty = selected_exercise.difficulty, 
                                                                        passed=False).count()
        
        error_index = None

        actual_output = ""
        if all(tests_passed):
            result = "Pasaste"
            ExerciseInstanceInGeneralPath.objects.create(user = self.request.user, 
                                                         exercise = selected_exercise, solution = code, passed = True)
        else:
            result = "Error "
            error_index = tests_passed.index(False)
            result += f" en el test-case {error_index + 1}: 'Expected Output':{selected_exercise.test_cases[error_index]['output']}"
            if failed_exercises < 1:
                ExerciseInstanceInGeneralPath.objects.create(user = self.request.user, 
                                                             exercise = selected_exercise, solution = code, passed = False)

            actual_output = stdout_list[error_index]
        
        ans = self.levelUp(request)
        num = ExerciseInstanceInGeneralPath.objects.filter(user=self.request.user, 
                                                           exercise__topic = selected_exercise.topic, 
                                                           exercise__difficulty = selected_exercise.difficulty, passed=True).count()
    
        if ans is not None:
            messages.success(request, ("Has subido de nivel a " + ans))
            return redirect("core:main_path")
        
        ctx = {'form': form, 'result': result, 'selected_exercise':selected_exercise, 'tema':selected_exercise.topic,"stdout": actual_output, "stderr": error_message, 'level':selected_exercise.difficulty, 'num':num}

        return render(request, self.template_name, ctx)
    



    def get_context_data(self, **kwargs: Any):
        context = super().get_context_data(**kwargs)
        
        pk = self.kwargs['pk']

        topic = get_object_or_404(Subject, pk=pk)

        excluded_exercise_id = ExerciseInstanceInGeneralPath.objects.filter(passed=True).values_list('exercise__id',flat=True)

        coding_exercises = Exercise.objects.filter(exercise_type=0, topic=topic, difficulty='Fácil', status=2).exclude(
            id__in=Subquery(excluded_exercise_id)
        )

        

        level_user_exists = CompletedLevelsPerUser.objects.filter(user=self.request.user, subject=topic).exists()

        if not level_user_exists:
            CompletedLevelsPerUser.objects.create(user = self.request.user, level="facil", subject = topic, skips=0)

        print(level_user_exists)

        user_level = CompletedLevelsPerUser.objects.filter(subject=topic, user=self.request.user).first()


        if user_level:
            l = user_level.level 
            coding_exercises = Exercise.objects.filter(exercise_type=0, topic=topic, difficulty=l, status=2).exclude(
            id__in=Subquery(excluded_exercise_id)
        )
            
            
        if user_level.level == 'Completado':
            print("ya entre")
            coding_exercises = Exercise.objects.filter(exercise_type=0, topic=topic, status=2).exclude(
            id__in=Subquery(excluded_exercise_id)
        )



        skips = CompletedLevelsPerUser.objects.filter(subject=topic, user=self.request.user, level=user_level.level)

        skip = skips[0].skips
        exercises = random.sample(list(coding_exercises), 1)
        
        passed_exercises = ExerciseInstanceInGeneralPath.objects.filter(user=self.request.user, 
                                                                        exercise__topic = topic, 
                                                                        exercise__difficulty = l, passed=True).count()
        self.request.session['selected_exercise_id'] = exercises[0].id
        context['subject'] = topic
        context['level'] = l
        context['coding_exercises'] = exercises
        context['skips'] = skip
        context['num'] = passed_exercises
        context['form'] = self.form_class()

        return context

    

