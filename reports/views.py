from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from utils.permissions import role_required
from appointments.models import Appointment
from medical_records.models import MedicalRecord
import csv
from datetime import datetime

@login_required
@role_required('ADMIN')
def reports_home(request):
    return render(request, 'reports/home.html')

@login_required
@role_required('ADMIN')
def export_appointments_excel(request):
    # Crear la respuesta con cabecera de archivo CSV
    respuesta = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    respuesta['Content-Disposition'] = f'attachment; filename="citas_{datetime.now().strftime("%Y%m%d")}.csv"'
    
    escritor = csv.writer(respuesta)
    escritor.writerow(['ID', 'Paciente', 'Medico', 'Especialidad', 'Fecha', 'Hora', 'Estado', 'Motivo'])
    
    # Traer todas las citas ordenadas de más reciente a más antigua
    citas = Appointment.objects.select_related(
        'patient__user', 'doctor__user', 'doctor__specialty'
    ).order_by('-date', '-time')
    
    for cita in citas:
        escritor.writerow([
            cita.id,
            cita.patient.user.get_full_name(),
            f"Dr. {cita.doctor.user.get_full_name()}",
            cita.doctor.specialty.name,
            cita.date.strftime('%Y-%m-%d'),
            cita.time.strftime('%H:%M'),
            cita.get_status_display(),
            cita.reason
        ])
    return respuesta

@login_required
def export_appointment_pdf(request, appointment_id):
    cita = get_object_or_404(Appointment, id=appointment_id)
    
    # Verificar que el usuario tenga permiso para ver esta cita
    if request.user.is_patient and cita.patient.user != request.user:
        return redirect('dashboard')
    if request.user.is_doctor and cita.doctor.user != request.user:
        return redirect('dashboard')
        
    return render(request, 'reports/print_appointment.html', {'appointment': cita})

@login_required
def export_medical_record_pdf(request, record_id):
    registro = get_object_or_404(MedicalRecord, id=record_id)
    
    # Solo el paciente dueño del registro puede verlo
    if request.user.is_patient and registro.patient.user != request.user:
        return redirect('dashboard')
        
    return render(request, 'reports/print_medical_record.html', {'record': registro})


