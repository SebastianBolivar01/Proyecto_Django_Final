from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from utils.permissions import role_required
from .models import Patient
from .forms import PatientForm
from appointments.models import Appointment
from medical_records.models import MedicalRecord

@login_required
def patient_list(request):
    # Lógica de lista basada en el rol del usuario
    if request.user.is_admin:
        # Administradores pueden ver a todos los pacientes
        pacientes = Patient.objects.select_related('user').all()
    elif request.user.is_doctor:
        # Los médicos solo ven pacientes con los que tienen citas
        pacientes = Patient.objects.filter(
            appointments__doctor=request.user.doctor_profile
        ).select_related('user').distinct()
    else:
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')
        
    busqueda = request.GET.get('q', '')
    if busqueda:
        # Búsqueda simple usando campos principales
        pacientes = pacientes.filter(
            Q(user__first_name__icontains=busqueda) |
            Q(user__last_name__icontains=busqueda) |
            Q(user__phone_number__icontains=busqueda) |
            Q(user__email__icontains=busqueda) |
            Q(blood_type__icontains=busqueda)
        )
        
    pacientes = pacientes.order_by('user__last_name', 'user__first_name')
    
    # Paginar de 10 en 10
    paginador = Paginator(pacientes, 10)
    numero_pagina = request.GET.get('page')
    pagina_actual = paginador.get_page(numero_pagina)
    
    return render(request, 'patients/patient_list.html', {
        'page_obj': pagina_actual,
        'query': busqueda
    })

@login_required
@role_required('ADMIN')
def patient_create(request):
    if request.method == 'POST':
        formulario = PatientForm(request.POST)
        if formulario.is_valid():
            paciente = formulario.save()
            messages.success(request, f"Paciente '{paciente.user.get_full_name()}' registrado exitosamente.")
            return redirect('patient_list')
        else:
            messages.error(request, "Error al registrar el paciente. Verifica los campos.")
    else:
        formulario = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': formulario, 'action': 'Registrar'})

@login_required
@role_required('ADMIN')
def patient_update(request, pk):
    paciente = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        formulario = PatientForm(request.POST, instance=paciente)
        if formulario.is_valid():
            paciente = formulario.save()
            messages.success(request, f"Datos del paciente '{paciente.user.get_full_name()}' actualizados exitosamente.")
            return redirect('patient_list')
        else:
            messages.error(request, "Error al actualizar los datos del paciente.")
    else:
        formulario = PatientForm(instance=paciente)
    return render(request, 'patients/patient_form.html', {'form': formulario, 'action': 'Editar'})

@login_required
@role_required('ADMIN')
def patient_delete(request, pk):
    paciente = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        nombre_completo = paciente.user.get_full_name()
        usuario_relacionado = paciente.user
        paciente.delete()
        usuario_relacionado.delete()
        messages.success(request, f"Paciente '{nombre_completo}' y su usuario asociado han sido eliminados.")
        return redirect('patient_list')
    return render(request, 'patients/patient_confirm_delete.html', {'patient': paciente})

@login_required
def patient_detail(request, pk):
    paciente = get_object_or_404(Patient, pk=pk)
    
    # Verificación de permisos básica
    if request.user.is_patient:
        if paciente.user != request.user:
            messages.error(request, "No tienes permiso para ver esta información.")
            return redirect('dashboard')
    elif request.user.is_doctor:
        # El médico puede ver al paciente solo si tienen consultas juntos
        tiene_cita = Appointment.objects.filter(
            patient=paciente, doctor=request.user.doctor_profile
        ).exists()
        if not tiene_cita:
            messages.error(request, "Este paciente no está asignado a tus consultas.")
            return redirect('patient_list')
            
    # Traer historial de citas y registros clínicos
    citas = Appointment.objects.filter(patient=paciente).order_by('-date', '-time')
    historias_clinicas = MedicalRecord.objects.filter(patient=paciente).order_by('-created_at')
    
    return render(request, 'patients/patient_detail.html', {
        'patient': paciente,
        'appointments': citas,
        'medical_records': historias_clinicas
    })
