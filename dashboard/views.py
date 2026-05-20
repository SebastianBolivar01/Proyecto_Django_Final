from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.db.models import Count
from patients.models import Patient
from doctors.models import Doctor, Specialty
from appointments.models import Appointment
from medical_records.models import MedicalRecord
import json

@login_required
def dashboard_home(request):
    usuario = request.user
    contexto = {}
    hoy = timezone.now().date()

    if usuario.is_admin:
        # Métricas generales para el administrador
        contexto['total_patients'] = Patient.objects.count()
        contexto['total_doctors'] = Doctor.objects.filter(is_active=True).count()
        contexto['appointments_today'] = Appointment.objects.filter(date=hoy).count()
        contexto['pending_appointments'] = Appointment.objects.filter(status='PENDING').count()
        
        # Gráfico: Citas por estado
        conteo_estados = Appointment.objects.values('status').annotate(count=Count('id'))
        etiquetas_estado = []
        datos_estado = []
        for item in conteo_estados:
            # Mapear código de estado a nombre legible
            mapa_estados = {'PENDING': 'Pendientes', 'CONFIRMED': 'Confirmadas', 'COMPLETED': 'Completadas', 'CANCELLED': 'Canceladas'}
            etiquetas_estado.append(mapa_estados.get(item['status'], item['status']))
            datos_estado.append(item['count'])
            
        contexto['status_labels_json'] = json.dumps(etiquetas_estado)
        contexto['status_data_json'] = json.dumps(datos_estado)

        # Gráfico: Médicos por especialidad
        conteo_especialidades = Specialty.objects.annotate(doc_count=Count('doctor')).filter(doc_count__gt=0)
        etiquetas_esp = [e.name for e in conteo_especialidades]
        datos_esp = [e.doc_count for e in conteo_especialidades]
        contexto['spec_labels_json'] = json.dumps(etiquetas_esp)
        contexto['spec_data_json'] = json.dumps(datos_esp)
        
        # Últimas citas para mostrar en la tabla del dashboard
        contexto['recent_appointments'] = Appointment.objects.select_related('patient__user', 'doctor__user').order_by('-date', '-time')[:5]

    elif usuario.is_doctor:
        # Métricas para el médico
        medico = usuario.doctor_profile
        contexto['appointments_today'] = Appointment.objects.filter(doctor=medico, date=hoy).count()
        contexto['pending_appointments'] = Appointment.objects.filter(doctor=medico, status='PENDING').count()
        contexto['total_patients'] = Patient.objects.filter(appointments__doctor=medico).distinct().count()
        
        # Próximas citas del médico
        contexto['upcoming_appointments'] = Appointment.objects.filter(
            doctor=medico, date__gte=hoy, status__in=['PENDING', 'CONFIRMED']
        ).select_related('patient__user').order_by('date', 'time')[:5]

    elif usuario.is_patient:
        # Métricas para el paciente
        paciente = usuario.patient_profile
        contexto['total_appointments'] = Appointment.objects.filter(patient=paciente).count()
        contexto['upcoming_appointments_count'] = Appointment.objects.filter(
            patient=paciente, date__gte=hoy, status__in=['PENDING', 'CONFIRMED']
        ).count()
        contexto['medical_records_count'] = MedicalRecord.objects.filter(patient=paciente).count()
        
        # Próximas citas del paciente
        contexto['upcoming_appointments'] = Appointment.objects.filter(
            patient=paciente, date__gte=hoy, status__in=['PENDING', 'CONFIRMED']
        ).select_related('doctor__user', 'doctor__specialty').order_by('date', 'time')[:5]

    return render(request, 'dashboard/home.html', contexto)


