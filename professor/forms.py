from django import forms
from core.models import Exercise, Assignment, AssignmentExerciseGroup, ExerciseTestCase, ExerciseChoice
from django.core.validators import RegexValidator
from django.utils.translation import gettext as _
from django.core.exceptions import ValidationError

from datetime import datetime


class MultipleChoiceExerciseForm(forms.ModelForm):
    '''Formulario para crear ejercicios de opción múltiple.
    '''
    class Meta:
        model = Exercise
        fields = ['author', 'title', 'description', 'topic', 'difficulty', 'answer', 'explanation']

        widgets = {
            'answer': forms.NumberInput(attrs={'min': 1, 'max': 20}),
        }
        
        labels = {
            'topic': 'Tema'
        }
        
        
class ExerciseChoiceForm(forms.ModelForm):
    '''Formulario para crear opciones de respuesta de un ejercicio de opción múltiple.
    '''
    class Meta:
        model = ExerciseChoice
        fields = ['text']


ExerciseChoiceFormSet = forms.inlineformset_factory(Exercise, ExerciseChoice, form=ExerciseChoiceForm, extra=0, min_num=1, validate_min=True)


class CodingExerciseForm(forms.ModelForm):
    '''Formulario para crear ejercicios de codificación.
    '''
    class Meta:
        model = Exercise
        fields = ['author', 'title', 'description', 'topic', 'difficulty']
        
        labels = {
            'topic': 'Tema'
        }
        
        
class ExerciseTestCaseForm(forms.ModelForm):
    '''Formulario para crear casos de prueba de un ejercicio de codificación.
    '''    
    class Meta:
        model = ExerciseTestCase
        fields = ['test_input', 'expected_output']
        
        widgets = {
            'test_input': forms.Textarea(attrs={'rows': 2}),
            'expected_output': forms.Textarea(attrs={'rows': 2})
        }


ExerciseTestCaseFormSet = forms.inlineformset_factory(Exercise, ExerciseTestCase, form=ExerciseTestCaseForm, extra=0, min_num=1, validate_min=True)


class MultipleExercisesForm(forms.Form):
    '''Formulario para crear múltiples ejercicios de cualquier tipo al mismo tiempo desde archivos JSON.
    '''
    exercise_files = forms.FileField(label='Archivos de ejercicios', widget=forms.ClearableFileInput(attrs={'multiple': True}))


class AssignmentForm(forms.ModelForm):
    '''Formulario para crear actividades en un curso.
    '''   
    class Meta:
        model = Assignment
        fields = ['name', 'due', 'feedback', 'attempts']

        widgets = {
            'due': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'attempts': forms.NumberInput(attrs={'min': 1, 'max': 10})
        }


class AssignmentExerciseGroupForm(forms.ModelForm):
    '''Formulario para crear un nuevo grupo de ejercicios dentro de una actividad de un curso.
    '''
    class Meta:
        model = AssignmentExerciseGroup
        fields = ['topic', 'difficulty', 'exercise_type', 'count']
        
        labels = {
            'topic': 'Tema'
        }
        
    def clean(self):
        '''Se sobrescribe el método clean para regresar un mensaje de error en caso de que se trate de crear una actividad con más ejercicios con las características solicitadas de los que hay disponibles. 
        '''
        cleaned_data = super().clean()
        count = cleaned_data.get('count')
        topic = cleaned_data.get('topic')
        exercise_type = cleaned_data.get('exercise_type')
        difficulty = cleaned_data.get('difficulty')
        
        if all([count, topic, difficulty]):
            exercises = Exercise.objects.filter(topic=topic, exercise_type=exercise_type, difficulty=difficulty, status=2)
            if count > len(exercises):
                self.add_error("count", f"No existen suficientes ejercicios, solo hay {len(exercises)} ejercicio(s) con las características solicitadas.")
                    

AssignmentExerciseGroupFormSet = forms.inlineformset_factory(Assignment, AssignmentExerciseGroup, form=AssignmentExerciseGroupForm, extra=0, min_num=1, validate_min=True)

