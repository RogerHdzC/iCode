from django.contrib import admin
from .models import Subject, SubjectRelation, Exercise
from django.urls import reverse
from django.utils.html import format_html
from .models import Exercise, ExerciseTestCase, ExerciseChoice, CompletedLevelsPerUser, ExerciseInstanceInGeneralPath, ExerciseInstanceInAssignment, Assignment, AssignmentExerciseGroup, Submission

from django.forms import Textarea
from django.db.models import CharField


class SubjectAdmin(admin.ModelAdmin):
    list_display = ['id', 'name']


class SubjectRelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'source', 'destination']


class TestCaseInline(admin.TabularInline):
    model = ExerciseTestCase
    
class ChoiceInline(admin.TabularInline):
    model = ExerciseChoice
    
    formfield_overrides = {
        CharField: {"widget": Textarea},
    }

class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'topic', 'exercise_type', 'difficulty', 'status', 'review_exercise']
    list_filter = ['topic', 'exercise_type', 'difficulty', 'status']
    readonly_fields = ['author']
    change_form_template = 'admin/change_form.html'
    inlines = [TestCaseInline, ChoiceInline]

    def review_exercise(self, obj):
        enlace = reverse('professor:review_exercise', args=[obj.id])
        return format_html('<a href="{}">Revisar Ejercicio</a>', enlace)

    review_exercise.allow_tags=True
    review_exercise.short_description = 'Revisión de Ejercicio'

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['review_exercise'] = self.review_exercise(Exercise.objects.get(id=object_id))
        return super().change_view(request, object_id, form_url, extra_context=extra_context)
    
    
class CompletedLevelsPerUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'level', 'subject', 'skips')


class ExerciseInstanceInGeneralPathAdmin(admin.ModelAdmin):
    list_display = ('user', 'exercise', 'solution', 'passed')


class ExerciseInstanceInAssignmentAdmin(admin.ModelAdmin):
    list_display = ('submission', 'exercise', 'solution', 'passed')


class AssignmentExerciseGroupInline(admin.TabularInline):
    model = AssignmentExerciseGroup


class AssignmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'course', 'due']
    inlines = [AssignmentExerciseGroupInline]


class ExerciseInstanceInline(admin.TabularInline):
    model = ExerciseInstanceInAssignment

class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['assignment', 'get_course', 'student', 'delivered']
    inlines = [ExerciseInstanceInline]
    
    @admin.display(description="Course")
    def get_course(self, obj):
        return obj.assignment.course

admin.site.register(ExerciseInstanceInAssignment, ExerciseInstanceInAssignmentAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(ExerciseInstanceInGeneralPath, ExerciseInstanceInGeneralPathAdmin)
admin.site.register(CompletedLevelsPerUser, CompletedLevelsPerUserAdmin)
admin.site.register(Exercise, ExerciseAdmin)
admin.site.register(Subject, SubjectAdmin)
admin.site.register(SubjectRelation, SubjectRelationAdmin)
admin.site.register(Submission, SubmissionAdmin)
