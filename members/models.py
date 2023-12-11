from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from .manager import CustomUserManager
from django.utils.translation import gettext as _

class CustomUser(AbstractUser):
    """La clase CustomUser es la que se encarga de crear nuestra tabla de usuario en la base de datos de Django, es donde nosotros modificamos al modelo de usuario por defecto de Django para poder añadirle los 
    elementos que para nuestro desarrollo son importantes, como su email, su rol, etc.
    Este modelo es utilizado en otros modulos como modelo base para los usuarios, ya sea que inicien sesion o se registren por primera vez"

    :param [AbstractUser]: [AbstractUser modelo de usuario por defecto de Django, este es modificado por nosotros añadiendole los elementos extras que son utiles para nuestro proyecto.]

    """
    
    STUDENT = 0
    PROFESSOR = 1

    ROLE_CHOICES = (
        (STUDENT, 'STUDENT'),
        (PROFESSOR, 'PROFESSOR')
    )
    username = None
    name = models.CharField('Nombre', max_length=50)
    last_name = models.CharField('Apellidos', max_length=100)
    role = models.PositiveSmallIntegerField('Rol', default=PROFESSOR, choices=ROLE_CHOICES, null=False)
    email = models.EmailField('Correo electrónico', validators = [RegexValidator(r"^[A-Za-z0-9_!#$%&'*+\/=?`{|}~^.-]+@tec\.mx$", message="Ingresa un correo valido del Tecnologico de Monterrey")], max_length=50, unique=True)
    verified = models.BooleanField('Cuenta verificada', default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email
    
