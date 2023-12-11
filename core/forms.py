from django import forms
from django_ace import AceWidget
from .models import ExerciseInstanceInGeneralPath, Exercise

class CodeInputForm(forms.Form):
    """La clase CodeInputForm es la clase utilizada para tener nuestro editor de codigo disponible en la pagina principal. Nosotros utilizamos el widget de Django, django-ace 
    para hacer uso de este editor de codigo, donde podemos especificar para que lenguaje de programacion lo necesitamos y elementos de diseño para su dispocision en la pagina principal.

    :param [forms.Form]: [Utilizamos forms.Form para poder darle un estilo a nuestro editor de codigo, ademas de darle un elemento de modo para que resalte la sintaxis, en este caso de Python]

    """

    code_input = forms.CharField(
        label='Ingresa tu código',
        widget=AceWidget(
            mode='python',
            showinvisibles=False,
            toolbar=False,
            fontsize='16px',
            width='100%',
        )
    )


class CodingExerciseInputForm(forms.ModelForm):

    class Meta:
        model = ExerciseInstanceInGeneralPath
        fields = ['solution']

        labels = {
            'solution': 'Ingresa tu Código'
        }

        widgets = {
            'solution': AceWidget(
                mode='python',
                showinvisibles=False,
                toolbar=False,
                fontsize='16px',
                width='100%'
            )
        }
        
