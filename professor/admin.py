from django.contrib import admin
from .models import Course


class CourseAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'created_by']

admin.site.register(Course, CourseAdmin)
 