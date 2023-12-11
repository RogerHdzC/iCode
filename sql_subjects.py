# Este script sirve para generar dos tablas de la base de datos referentes a los temas posibles para cada ejercicio y las dependencias entre estos temas

# Comando para ejecutar este script desde la carpeta base del proyecto:
# python3 manage.py shell < sql_subjects.py

from core.models import Subject, SubjectRelation

try:
    subject_list = [
    Subject(id='1.1', name='1.1 Uso de programación para la solución de problemas'),
    Subject(id='1.2', name='1.2 Lenguajes de programación'),
    Subject(id='1.3', name='1.3 Fases de desarrollo de un programa'),
    Subject(id='1.4', name='1.4 Ambientes de programación'),
    Subject(id='2.1', name='2.1 Estructura básica de un programa secuencial.'),
    Subject(id='2.2', name='2.2 Variables, constantes y tipos de datos'),
    Subject(id='2.3', name='2.3 Expresiones aritméticas'),
    Subject(id='2.4', name='2.4 Funciones predefinidas'),
    Subject(id='2.5', name='2.5 Solución de problemas con fórmulas matemáticas'),
    Subject(id='3.1', name='3.1 Programación modular'),
    Subject(id='3.2', name='3.2 Funciones'),
    Subject(id='3.3', name='3.3 Solución de problemas con funciones'),
    Subject(id='4.1', name='4.1 Expresiones lógicas'),
    Subject(id='4.2', name='4.2 Estatus de decisión'),
    Subject(id='4.3', name='4.3 Estatutos de decisión anidados'),
    Subject(id='4.4', name='4.4 Solución de problemas con estatutos de decisión'),
    Subject(id='5.1', name='5.1 While'),
    Subject(id='5.2', name='5.2 For'),
    Subject(id='5.3', name='5.3 Ciclos anidados'),
    Subject(id='5.4', name='5.4 Solución de problemas con estatutos de repetición'),
    Subject(id='6.1', name='6.1 Listas'),
    Subject(id='6.2', name='6.2 Recorridos de listas'),
    Subject(id='6.3', name='6.3 Matrices'),
    Subject(id='6.4', name='6.4 Strings'),
    Subject(id='6.5', name='6.5 Solución de problemas con listas'),
    Subject(id='6.6', name='6.6 Solución de problemas con matrices'),
    Subject(id='6.7', name='6.7 Solución de problemas con strings'),
    Subject(id='7.1', name='7.1 Creación y uso de archivos'),
    Subject(id='7.2', name='7.2 Solución de problemas con archivos')
    ]
except Exception as e:
    print('subject_list: ', e)

try:
    Subject.objects.bulk_create(subject_list)
except Exception as e:
    print('subjects: ', e)

try:
    relation_list = [
    SubjectRelation(source=Subject.objects.get(id='1.1'), destination=Subject.objects.get(id='1.2')),
    SubjectRelation(source=Subject.objects.get(id='1.1'), destination=Subject.objects.get(id='1.3')),
    SubjectRelation(source=Subject.objects.get(id='1.2'), destination=Subject.objects.get(id='1.4')),
    SubjectRelation(source=Subject.objects.get(id='1.3'), destination=Subject.objects.get(id='2.1')),
    SubjectRelation(source=Subject.objects.get(id='2.1'), destination=Subject.objects.get(id='2.2')),
    SubjectRelation(source=Subject.objects.get(id='2.2'), destination=Subject.objects.get(id='2.3')),
    SubjectRelation(source=Subject.objects.get(id='2.2'), destination=Subject.objects.get(id='2.4')),
    SubjectRelation(source=Subject.objects.get(id='2.2'), destination=Subject.objects.get(id='3.1')),
    SubjectRelation(source=Subject.objects.get(id='2.2'), destination=Subject.objects.get(id='4.1')),
    SubjectRelation(source=Subject.objects.get(id='2.4'), destination=Subject.objects.get(id='2.5')),
    SubjectRelation(source=Subject.objects.get(id='3.1'), destination=Subject.objects.get(id='3.2')),
    SubjectRelation(source=Subject.objects.get(id='3.2'), destination=Subject.objects.get(id='3.3')),
    SubjectRelation(source=Subject.objects.get(id='4.1'), destination=Subject.objects.get(id='4.2')),
    SubjectRelation(source=Subject.objects.get(id='4.2'), destination=Subject.objects.get(id='4.3')),
    SubjectRelation(source=Subject.objects.get(id='4.3'), destination=Subject.objects.get(id='4.4')),
    SubjectRelation(source=Subject.objects.get(id='4.4'), destination=Subject.objects.get(id='5.1')),
    SubjectRelation(source=Subject.objects.get(id='4.4'), destination=Subject.objects.get(id='5.2')),
    SubjectRelation(source=Subject.objects.get(id='5.1'), destination=Subject.objects.get(id='5.3')),
    SubjectRelation(source=Subject.objects.get(id='5.2'), destination=Subject.objects.get(id='5.3')),
    SubjectRelation(source=Subject.objects.get(id='5.3'), destination=Subject.objects.get(id='5.4')),
    SubjectRelation(source=Subject.objects.get(id='5.4'), destination=Subject.objects.get(id='6.1')),
    SubjectRelation(source=Subject.objects.get(id='5.4'), destination=Subject.objects.get(id='6.4')),
    SubjectRelation(source=Subject.objects.get(id='5.4'), destination=Subject.objects.get(id='7.1')),
    SubjectRelation(source=Subject.objects.get(id='6.1'), destination=Subject.objects.get(id='6.2')),
    SubjectRelation(source=Subject.objects.get(id='6.2'), destination=Subject.objects.get(id='6.3')),
    SubjectRelation(source=Subject.objects.get(id='6.2'), destination=Subject.objects.get(id='6.5')),
    SubjectRelation(source=Subject.objects.get(id='6.3'), destination=Subject.objects.get(id='6.6')),
    SubjectRelation(source=Subject.objects.get(id='6.4'), destination=Subject.objects.get(id='6.7')),
    SubjectRelation(source=Subject.objects.get(id='7.1'), destination=Subject.objects.get(id='7.2'))
    ]
except Exception as e:
    print('relation_list: ', e)

try:
    SubjectRelation.objects.bulk_create(relation_list)
except Exception as e:
    print('subject_relations: ', e)

