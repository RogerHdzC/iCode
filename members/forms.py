from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth.password_validation import password_validators_help_text_html
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    """La clase CustomUserCreationForm es la clase que nosotros creamos para poder hacer uso de nuestro propio formulario con el objetivo
    de registrar usuarios en la plataforma. Este hereda del formulario por defecto de Django que es UserCreationForm, y nosotros lo modificamos
    para que reconozca con que modelo estara trabajando de ahora en adelante"

    :param [UserCreationForm]: [UserCreationForm es el formulario por defecto de Django, este se hereda en esta clase para que pueda ser modificado y vinculado a nuestro modelo personalizado]

    """
    password1 = forms.CharField(
        label = 'Contraseña',
        widget = forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip = False,
        help_text = password_validators_help_text_html(),
    )

    password2 = forms.CharField(
        label = 'Verificar Contraseña',
        widget = forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        strip = False,
        help_text = _('Ingresa tu contraseña de nuevo para verificarla.'),
    )

    class Meta:
        model = CustomUser
        fields = ('email', 'name', 'last_name',)
        

class CustomUserChangeForm(UserChangeForm):
    """La clase CustomUserChangeForm es la clase que nosotros creamos para poder hacer uso de nuestro propio formulario con el objetivo
    de editar elementos de los usuarios dentro de la plataforma. Este hereda del formulario por defecto de Django que es UserChangeForm, y 
    nosotros lo modificamos para que reconozca con que modelo estara trabajando de ahora en adelante"

    :param [UserChangeForm]: [UserChangeForm es el formulario por defecto de Django, este se hereda en esta clase para que pueda ser modificado y vinculado a nuestro modelo personalizado]

    """

    class Meta:
        model = CustomUser
        fields = '__all__'
