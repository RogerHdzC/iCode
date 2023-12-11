from django.urls import path
from django.views.generic.list import ListView
from . import views

app_name = 'professor'

urlpatterns = [
    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('new_course/', views.CourseCreateView.as_view(), name='new_course'),
    path('delete_course/<uuid:pk>', views.CourseDeleteView.as_view(), name='delete_course'),
    path('course_students/<uuid:pk>', views.CourseStudentsView.as_view(), name='course_students'),
    path('course_assignments/<uuid:pk>', views.CourseAssignmentsView.as_view(), name='course_assignments'),
    path('delete_enrollment/<uuid:course_id>/<int:student_id>', views.EnrollmentDeleteView.as_view(), name='delete_enrollment'),
    path('delete_assignment/<int:pk>', views.AssignmentDeleteView.as_view(), name='delete_assignment'),
    path('my_exercises/', views.ExerciseListView.as_view(), name='my_exercises'),
    path('new_multiple_choice/', views.MultipleChoiceExerciseCreateView.as_view(), name='new_multiple_choice'),
    path('update_multiple_choice/<uuid:pk>', views.MultipleChoiceExerciseUpdateView.as_view(), name='update_multiple_choice'),
    path('new_coding/', views.CodingExerciseCreateView.as_view(), name='new_coding'),
    path('update_coding/<uuid:pk>', views.CodingExerciseUpdateView.as_view(), name='update_coding'),
    path('delete_exercise/<uuid:pk>', views.ExerciseDeleteView.as_view(), name='delete_exercise'),
    path('new_assignment/<uuid:course_id>/', views.AssignmentCreateView.as_view(), name='new_assignment'),
    path('assignment_submissions/<int:pk>', views.AssignmentSubmissionsView.as_view(), name='assignment_submissions'),
    path('submission_detail/<int:assignment_id>/<int:student_id>', views.SubmissionDetailView.as_view(), name='submission_detail'),
    path('review_exercise/<uuid:pk>', views.ReviewExercise.as_view(), name='review_exercise'),
    path('add_multiple_exercises/', views.AddMultipleExercisesView.as_view(), name='add_multiple_exercises'),
]
