from django.urls import path
from . import views

app_name = 'core'
urlpatterns = [
    path('', views.HomeView.as_view(), name='code'),
    # ~ path('main_path/', views.GraphView.as_view(), name='main_path'),
    # ~ path('subject/<str:pk>/', views.SubjectDetailView.as_view(), name='subject'),
    # ~ path('actualizar-skips/', views.actualizar_skips, name="actualizar-skips"),
]
