from django.db import models
from django.conf import settings
import uuid


class Course(models.Model):
    '''
    Este modelo representa un curso al cual se pueden inscribir los estudiantes. Está asociado a un profesor mediante el campo "admin" y a múltiples estudiantes mediante el campo "students".
    '''
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField('Nombre', max_length=50)
    students = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='courses', through='Enrollment')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Enrollment(models.Model):
    '''
    Este modelo representa la inscripción de un estudiante en un curso. Es una tabla intermedia que se utiliza para conectar los modelos "Course" y "CustomUser".
    '''
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    unique_together = ['student', 'course']

