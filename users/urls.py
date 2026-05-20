from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', views.register_patient, name='register'),
    
    # User management for Administrators
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/toggle/', views.user_toggle_status, name='user_toggle_status'),
]
