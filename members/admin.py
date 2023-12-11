from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser

class CustomUserAdmin(UserAdmin):
    """La clase CustomUserAdmin utiliza al admin de Django para poder hacerle las modificaciones necesarias el modelo
    de usuario que nosotros creamos. Aqui se definen los formularios que Django debe de utilizar para este tipo de
    usuarios, asi como que campos podran ser visibles y editables desde la pagina de admin de Django. Al final, registramos 
    los elementos para que la pagina de administrador de Django reconozca los cambios realizados

    :param [UserAdmin]: [UserAdmin es el administrador por defecto de Django, nosotros lo heredamos para poder hacer las modificaciones necesarias para nuestro modelo custom]

    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm

    model = CustomUser

    list_display = ('email', 'name', 'last_name','role',)
    
    #list_filter = ('is_active', 'is_staff', 'is_superuser')

    fieldsets = (
        ('Personal Info', {'fields': ('email', 'password', 'role')}),
        ('Permissions', {'fields': ('is_staff', 'is_active',
         'is_superuser', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login', 'date_joined')})
    )

    add_fieldsets = (
        ('Personal Info', {
            'classes': ('wide',),
            'fields': ('name', 'last_name', 'email', 'role', 'password1', 'password2', 'is_staff', 'is_active')}
         ),
    )

    search_fields = ('email',)
    ordering = ('email',)

admin.site.register(CustomUser, CustomUserAdmin)
