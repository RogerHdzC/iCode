from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from core.models import Subject, CompletedLevelsPerUser
from .forms import CustomUserCreationForm
from .models import CustomUser

import re

def test_email(request):
    """Esta función solo existe para probar la funcionalidad de enviar correos.
    """
    send_mail(
        "Subject here",
        "Here is the message.",
        "icode.itesm@gmail.com",
        ["test_email@tec.mx"],
        fail_silently=False,
    )
    return render(request, 'core/home.html')
    
def login_user(request):
    """La funcion login_user dentro de nuestro modulo de vistas tiene la funcionalidad de realizar el proceso de inicio de sesion para los usuarios. Primero 
    requiere conocer que tipo de metodo el usuario esta enviando desde la request, si es POST se procede a obtener tanto su email como su correo, que son los elementos que lo identifican en nuestra base de datos,
    se autentica al usuario con el metodo de autenticacion de Django, y si no existen problemas con su solicitud, se inicia sesion de manera ordinaria y se redirecciona a la pagina principal.

    En caso de exista algun error, se envía un mensaje para que lo intente nuevamente.
    En caso de que sea la primera vez que el usuario entra a la pagina de login, simplemente se procese a mandar a renderizar el archivo html para que lo llene.

    :param [request]: [Request es el nombre comun en Django para mencionar a un HttpRequest que es enviado con todos los metadatos de esta solicitud, se obtiene y se procesa]
    """

    if request.user.is_authenticated:
        return redirect('core:code')
    if request.method == "POST":
        email = request.POST['username']
        if is_student(email):
            email = 'A' + email[1:]
        password = request.POST['password']
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:code')
        else:
            messages.success(
                request, ('Hubo un error en tu login, intentalo nuevamente...'))
            return redirect('login')
    else:
        return render(request, 'authenticate/login.html', {})


@login_required
def logout_user(request):
    """La funcion de logout_user dentro de nuestro modulo de vistas se encarga de realizar el cierre de sesion de un usuario. Se utilizan los modulos por defecto de Django para poder realizar esto.
    Se obtiene desde la request y con el modulo logout un cierre de sesion del usuario, se da un mensaje de exito y se redirecciona a la pagina principal.

    :param [request]: [Request es el nombre comun en Django para mencionar a un HttpRequest que es enviado con todos los metadatos de esta solicitud, se obtiene y se procesa]
    """
    logout(request)
    messages.success(request, ('Has hecho logout exitosamente!'))
    return redirect('login')


def validate_email_address(email_address):
   """La funcion de validate_email_address dentro de nuestro modulo de vistas se encarga de realizar la comprobacion con funciones RegEx de si un correo enviado en una solicitud de registro cumple con las condiciones para 
   ser considerado un email valido.

    :param [email_address]: [String que contiene el email del usuario]
    """
   return re.search(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@tec.mx$", email_address)


def is_student(email_address):
    """La funcion is_student dentro de nuestro modulo de vistas se encarga de realizar la comprobacion con funciones RegEx de si un correo enviado en una solicitud de registro cumple con las condiciones para
   ser considerado email de alumno, comenzar con la letra A y seguir de 8 numeros.

    :param [email_address]: [String que contiene el email del usuario]
    """
    return re.search(r"^[Aa][0-9]{8}@tec.mx$", email_address)

def register_user(request):
    """La funcion de register_user dentro de nuestro modulo de vistas se encarga de realizar el registro de nuevos usuarios a la plataforma. Primero se comprueba el metodo con el que 
    se envia la solicitud, en caso de set POST se obtienen los elementos identificadores del usuario, su email y su contraseña. Despues se utilizan las funciones por defecto de Django de autenticacion
    para despues registrar al usuario.

    Es en este punto donde se realiza el analisis de los email de los usuarios nuevos, y se determina su rol en la pagina, en caso de ser alumnos, usando la funcion "is_student"
    podemos obtener el rol del usuario, y modificarlo para que en nuestra base de datos se vea reflejado, ya sea de un estudiante o de un profesor.

    :param [request]: [Request es el nombre comun en Django para mencionar a un HttpRequest que es enviado con todos los metadatos de esta solicitud, se obtiene y se procesa]
    """
    if request.user.is_authenticated:
        return redirect('core:code')
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            email = form.cleaned_data['email']
            password = form.cleaned_data['password1']
            user = authenticate(email=email, password=password)
            login(request, user)
            if is_student(email):
                # Se asegura que la primera letra del correo se guarde como mayúscula
                user.email = 'A' + email[1:]
                user.role = 0
                user.save()
            else:
                user.role = 1
                user.save()
                
            messages.success(request, ("Registro exitoso!"))
            return redirect('core:code')
    else:
        form = CustomUserCreationForm()

    return render(request, 'authenticate/register.html', {
        "form": form,
    })
