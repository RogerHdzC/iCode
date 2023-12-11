from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext as _

class CustomUserManager(BaseUserManager):
    """La clase CustomUserManager es una clase de igual manera creada para poder hacer uso del modelo personalizado de usuario que creamos. En este caso en especifico está hereda de la clase BaseUserManager, clase por defecto de Django para manejar a los usuarios. En esta clase nosotros modificamos que el campo unico que identifique a nuestros usuarios sea su email, no su nombre de usuario."

    :param [BaseUserManager]: [BaseUserManager es el manager por defecto de Django para su modelo de usuario, nosotros lo heredamos para poder modificarlo y especificar campos importantes para nosotros]

    """

    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_('Users must have an email address'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
