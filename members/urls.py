from django.urls import path, include
from django.contrib.auth.views import (
    LogoutView,
    PasswordResetView,
    PasswordResetDoneView,
    PasswordResetConfirmView,
    PasswordResetCompleteView
)
from . import views

urlpatterns = [
    path('login_user/', views.login_user, name='login'),
    path('logout_user/', views.logout_user, name='logout'),
    path('register_user/', views.register_user, name='register'),

    path('password_reset/', PasswordResetView.as_view(
        template_name='authenticate/password_reset_form.html'), name='password_reset'),
    path('password_reset_done/', PasswordResetDoneView.as_view(
        template_name='authenticate/password_reset_done.html'), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
        template_name='authenticate/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset_complete/', PasswordResetCompleteView.as_view(
        template_name='authenticate/password_reset_complete.html'), name='password_reset_complete'),
        
    path('test_email/', views.test_email, name='test_email')

]
