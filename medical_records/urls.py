from django.urls import path
from . import views

urlpatterns = [
    path('', views.medical_record_list, name='medical_record_list'),
    path('create/<int:patient_id>/', views.medical_record_create, name='medical_record_create'),
    path('<int:pk>/update/', views.medical_record_update, name='medical_record_update'),
    path('<int:pk>/detail/', views.medical_record_detail, name='medical_record_detail'),
]
