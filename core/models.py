from django.db import models
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from professor.models import Course

import json
import uuid
from datetime import timedelta, datetime


DIFFICULTY_CHOICES = (
    ("facil", "Fácil"),
    ("media", "Media"),
    ("dificil", "Difícil")
)

class Subject(models.Model):
    """El modelo Subject son los temas que forman parte de la ruta general de aprendizaje. El modelo cuenta con un campo nombre y una funcion 
    que regresa el nombre del tema.
    """
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField('Nombre', max_length=255)

    def __str__(self):
        return self.name


class SubjectRelation(models.Model):
    '''
    El modelo SubjectRelation representa la relación que existe entre los temas de la ruta general. Al ser un grafo se decidió utilizar un sistema
    de llaves foraneas que ayuden a identificar el nodo fuente del nodo destino y asi poder representarlos posteriormente
    '''
    source = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="from_relation")
    destination = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="to_relation")


class Exercise(models.Model):
    '''Representa los campos comunes de un ejercicio que puede ser subido a la plataforma por un profesor 
    y resuelto por estudiantes en la ruta general de aprendizaje o en assignments específicos de un curso.
    '''
    REJECTED = 0
    IN_REVIEW = 1
    ACCEPTED = 2

    STATUS_CHOICES = (
        (REJECTED, 'RECHAZADO'),
        (IN_REVIEW, 'EN REVISIÓN'),
        (ACCEPTED, 'ACEPTADO')
    )
    
    CODE = 0
    CHOICE = 1
    
    TYPE_CHOICES = (
        (CODE, 'Código'),
        (CHOICE, 'Opción múltiple')
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    author = models.CharField('Autor', max_length=50)
    title = models.CharField('Título', max_length=100)
    description = models.TextField('Descripción', max_length=1000)
    topic = models.ForeignKey(Subject, verbose_name='Tema', on_delete=models.SET_NULL, null=True)
    difficulty = models.CharField('Dificultad', max_length=7, choices=DIFFICULTY_CHOICES, default='media')
    exercise_type = models.PositiveSmallIntegerField('Tipo de ejercicio', default=CODE, choices=TYPE_CHOICES, null=False)
    answer = models.PositiveSmallIntegerField(
        'Respuesta correcta',
        default=1,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ],
        null=True
    )
    explanation = models.CharField('Explicación', max_length=500, blank=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Creado por', on_delete=models.DO_NOTHING)
    status = models.PositiveSmallIntegerField('Estatus', default=IN_REVIEW, choices=STATUS_CHOICES, null=False)
    status_message = models.TextField('Mensaje del administrador', null=False, blank=True, default="")
    
    def __str__(self):
        return self.title


class ExerciseChoice(models.Model):
    '''Representa una de las opciones posibles en un ejercicio de opción múltiple.
    '''
    text = models.CharField('Texto', max_length=500)
    exercise = models.ForeignKey(Exercise, verbose_name='Ejercicio', on_delete=models.CASCADE, related_name='options')
    
    class Meta:
        ordering = ['id']
    
    def __str__(self):
        return self.text

    
def validate_no_single_quotes(text):
    if text.startswith("'") or text.endswith("'"):
        raise ValidationError('El texto no debe comenzar ni terminar con comillas sencillas.')

class ExerciseTestCase(models.Model):
    '''Representa un caso de prueba en un ejercicio de codificación.
    '''
    exercise = models.ForeignKey(Exercise, verbose_name='Ejercicio', on_delete=models.CASCADE, related_name='test_cases')
    test_input = models.TextField('Entrada', max_length=500, blank=True, validators=[validate_no_single_quotes])
    expected_output = models.TextField('Resultado esperado', max_length=500, blank=True, validators=[validate_no_single_quotes])
    
    def __str__(self):
        return f'{self.test_input} -> {self.expected_output}'


# ~ def default_due_date():
    # ~ due = datetime.now()
    # ~ return due.replace(hour=23, minute=59)
    
class Assignment(models.Model):
    '''
    Representa una tarea o examen creado por un profesor para un curso específico.
    '''
    NO_FEEDBACK = 0
    HOW_MANY_PASSED = 1
    SHOW_TEST_CASES = 2
    
    FEEDBACK_CHOICES = (
        (NO_FEEDBACK, 'Sin retroalimentación'),
        (HOW_MANY_PASSED, 'Mostrar cuántos casos de prueba pasaron'),
        (SHOW_TEST_CASES, 'Mostrar detalles de cuáles casos de prueba pasaron')
    )
    
    name = models.CharField('Nombre', max_length=100)
    course = models.ForeignKey(Course, verbose_name='Curso', on_delete=models.CASCADE)
    feedback = models.PositiveSmallIntegerField('Nivel de retroalimentación', default=HOW_MANY_PASSED, choices=FEEDBACK_CHOICES)
    due = models.DateTimeField('Fecha de entrega')
    duration = models.DurationField('Tiempo límite', default=timedelta(minutes=60))
    attempts = models.PositiveSmallIntegerField(
        'Intentos permitidos',
        default=3,
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ])
    
    def __str__(self):
        return self.name
    

class AssignmentExerciseGroup(models.Model):
    '''
    Representa una sección de los ejercicios de un assignment. Incluye el número de ejercicios en la sección y el assignment al que está asociado, así como el tema y dificultad de los ejercicios.
    '''
    CODE = 0
    CHOICE = 1
    
    TYPE_CHOICES = (
        (CODE, 'Código'),
        (CHOICE, 'Opción múltiple')
    )
    
    count = models.PositiveSmallIntegerField('Número de ejercicios', validators=[MinValueValidator(1), MaxValueValidator(100)])
    assignment = models.ForeignKey(Assignment, verbose_name='Actividad', on_delete=models.CASCADE)
    difficulty = models.CharField('Dificultad', max_length=7, choices=DIFFICULTY_CHOICES, default='media')
    topic = models.ForeignKey(Subject, verbose_name='Tema', on_delete=models.SET_NULL, null=True)
    exercise_type = models.PositiveSmallIntegerField('Tipo de ejercicios', default=CODE, choices=TYPE_CHOICES, null=False)

    
class Submission(models.Model):
    '''Representa una entrega de una actividad por un estudiante.
    '''
    assignment = models.ForeignKey(Assignment, verbose_name='Actividad', on_delete=models.CASCADE)
    student = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Estudiante', on_delete=models.CASCADE)
    start_time = models.DateTimeField('Tiempo de inicio', default=None, null=True)
    submit_time = models.DateTimeField('Tiempo de entrega', default=None, null=True)
    delivered = models.BooleanField('Entregado', default=False)
    grade = models.FloatField('Calificación', default=0,  validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    def is_active(self):
        return (timezone.now() - self.start_time) < self.total_duration
    
    class Meta:
        ordering = ['submit_time']
    
    
class CompletedLevelsPerUser(models.Model):
    '''
    Modelo que se encarga de controlar los niveles completados por el usuario y de subirlo de nivel al completar 
    el requisito deseado.
    '''
    LEVEL = (
        ("facil", "Facil"),
        ("media", "Intermedio"),
        ("dificil", "Dificil"), 
        ("Completado", "Completado") 
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuario', on_delete=models.CASCADE)
    level = models.CharField('Nivel', max_length=20, choices=LEVEL, default='Facil')
    subject = models.ForeignKey(Subject, verbose_name='Tema', on_delete=models.CASCADE)
    skips = models.IntegerField('Saltos disponibles', default=0, validators=[MaxValueValidator(3)])


class ExerciseInstanceInGeneralPath(models.Model):
    '''Representa una instancia de un ejercicio resuelto dentro de la ruta general de aprendizaje.
    '''
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Usuario', on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, verbose_name='Ejercicio', on_delete=models.CASCADE)
    solution = models.TextField('Solución')
    passed = models.BooleanField(default=False)


class ExerciseInstanceInAssignment(models.Model):
    '''Representa una instancia de un ejercicio resuelto dentro de una actividad de un curso.
    '''
    exercise = models.ForeignKey(Exercise, verbose_name='Ejercicio', on_delete=models.CASCADE)
    submission = models.ForeignKey(Submission, verbose_name='Entrega', on_delete=models.CASCADE, related_name='exercise_instances')
    solution = models.TextField('Solución')
    passed = models.BooleanField('¿Correcto?', default=False)
