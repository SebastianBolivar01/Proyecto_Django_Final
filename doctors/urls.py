from django.urls import path
from . import views

urlpatterns = [
    path('', views.doctor_list, name='doctor_list'),
    path('create/', views.doctor_create, name='doctor_create'),
    path('<int:pk>/update/', views.doctor_update, name='doctor_update'),
    path('<int:pk>/delete/', views.doctor_delete, name='doctor_delete'),
    
    # Specialty CRUD
    path('specialties/', views.specialty_list, name='specialty_list'),
    path('specialties/create/', views.specialty_create, name='specialty_create'),
    path('specialties/<int:pk>/update/', views.specialty_update, name='specialty_update'),
    path('specialties/<int:pk>/delete/', views.specialty_delete, name='specialty_delete'),
]
