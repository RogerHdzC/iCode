from django import forms
from core.models import ExerciseInstanceInAssignment
from django_ace import AceWidget

class CourseJoinForm(forms.Form):
    '''Formulario utilizado para la inscripción de un estudiante en un curso mediante el id del curso.
    '''
    course_id = forms.CharField(label="ID Curso", max_length=36)


class CodingExerciseSolveForm(forms.ModelForm):
    '''Formulario para resolver un ejercicio de codificación en una actividad.
    '''
    solution = forms.CharField(label='', error_messages={'required': 'Te falta contestar este ejercicio.'}, widget=AceWidget(
        mode='python',
        showinvisibles=False,
        toolbar=False,
        fontsize='16px',
        width='100%',
    ))
    
    class Meta:
        model = ExerciseInstanceInAssignment
        fields = ['solution']
        
        
class MultipleChoiceExerciseSolveForm(forms.ModelForm):
    '''Formulario para resolver un ejercicio de opción múltiple en una actividad.
    '''
    solution = forms.ChoiceField(label='', error_messages={'required': 'Te falta contestar este ejercicio.'}, widget=forms.RadioSelect(attrs={'class': 'radio'}))
    
    class Meta:
        model = ExerciseInstanceInAssignment
        fields = ['solution']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print('self.instance', self.instance)
        print('type', type(self.instance))
        options = self.instance.exercise.options.all()
        choices = [(n, option) for n, option in enumerate(options, start=1)]
        self.fields['solution'].choices = choices


CodingSolveFormSet = forms.modelformset_factory(ExerciseInstanceInAssignment, form=CodingExerciseSolveForm, extra=0, min_num=0, edit_only=True)
MultipleChoiceSolveFormSet = forms.modelformset_factory(ExerciseInstanceInAssignment, form=MultipleChoiceExerciseSolveForm, extra=0, min_num=0, edit_only=True)


class CodingExerciseReviewForm(forms.ModelForm):
    '''Formulario para revisar las respuestas a un ejercicio de codificación de un estudiante en una actividad.
    '''
    solution = forms.CharField(label='Código ingresado', required=False, widget=AceWidget(
        mode='python',
        showinvisibles=False,
        toolbar=False,
        fontsize='16px',
        width='100%',
        readonly = True
    ))
    
    class Meta:
        model = ExerciseInstanceInAssignment
        fields = ['solution']


class MultipleChoiceExerciseReviewForm(forms.ModelForm):
    '''Formulario para revisar las respuestas a un ejercicio de opción múltiple de un estudiante en una actividad.
    '''
    solution = forms.ChoiceField(label='Opción elegida', required=False, widget=forms.RadioSelect(attrs={'class': 'radio', 'disabled': True}))
    
    class Meta:
        model = ExerciseInstanceInAssignment
        fields = ['solution']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = self.instance.exercise.options.all()
        choices = [(n, option) for n, option in enumerate(options, start=1)]
        selected_answer = self.instance.solution
        self.fields['solution'].choices = choices
        self.fields['solution'].default = selected_answer
    

CodingReviewFormSet = forms.modelformset_factory(ExerciseInstanceInAssignment, form=CodingExerciseReviewForm, extra=0, min_num=1)
MultipleChoiceReviewFormSet = forms.modelformset_factory(ExerciseInstanceInAssignment, form=MultipleChoiceExerciseReviewForm, extra=0, min_num=1)
