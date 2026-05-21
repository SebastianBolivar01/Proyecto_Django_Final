from django.urls import path
from . import views

urlpatterns = [
    path('', views.reports_home, name='reports_home'),
    path('excel/appointments/', views.export_appointments_excel, name='export_appointments_excel'),
    path('pdf/appointment/<int:appointment_id>/', views.export_appointment_pdf, name='export_appointment_pdf'),
    path('pdf/medical-record/<int:record_id>/', views.export_medical_record_pdf, name='export_medical_record_pdf'),
]
