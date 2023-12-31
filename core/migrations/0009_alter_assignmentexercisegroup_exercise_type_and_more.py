# Generated by Django 4.2 on 2023-08-22 02:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_assignmentexercisegroup_exercise_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='assignmentexercisegroup',
            name='exercise_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Código'), (1, 'Opción múltiple')], default=0, verbose_name='Tipo de ejercicios'),
        ),
        migrations.AlterField(
            model_name='exercise',
            name='exercise_type',
            field=models.PositiveSmallIntegerField(choices=[(0, 'Código'), (1, 'Opción múltiple')], default=0, verbose_name='Tipo de ejercicio'),
        ),
    ]
