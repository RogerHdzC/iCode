# Generated by Django 4.2 on 2023-08-25 20:16

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_remove_assignment_hints_assignment_feedback_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='submission',
            name='grade',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(100)], verbose_name='Calificación'),
        ),
    ]