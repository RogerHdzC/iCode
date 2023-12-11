from django.urls import path
from django.views.generic.list import ListView
from . import views

app_name = 'student'
urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('join_course', views.join_course, name='join_course'),
    path('course_assignments/<uuid:pk>', views.CourseAssignmentsView.as_view(), name='course_assignments'),
    path('new_submission/<int:assignment_id>', views.SubmissionCreateView.as_view(), name='new_submission'),
    path('review_submission/<int:assignment_id>>', views.ReviewSubmissionView.as_view(), name='review_submission'),
    path('test-code/', views.test_code_view, name="test_code_view"),
    path('time-out/', views.time_out, name="time_out"),
]
