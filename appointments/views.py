from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.db.models import Q
from utils.permissions import role_required
from .models import Appointment
from .forms import AppointmentForm

@login_required
def appointment_list(request):
    # Filtrar citas según el rol del usuario
    if request.user.is_admin:
        citas = Appointment.objects.select_related('patient__user', 'doctor__user', 'doctor__specialty').all()
    elif request.user.is_doctor:
        citas = Appointment.objects.filter(doctor=request.user.doctor_profile).select_related('patient__user', 'doctor__user', 'doctor__specialty')
    elif request.user.is_patient:
        citas = Appointment.objects.filter(patient=request.user.patient_profile).select_related('patient__user', 'doctor__user', 'doctor__specialty')
    else:
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    # Filtros de búsqueda en la UI
    filtro_estado = request.GET.get('status', '')
    if filtro_estado:
        citas = citas.filter(status=filtro_estado)
        
    busqueda = request.GET.get('q', '')
    if busqueda:
        citas = citas.filter(
            Q(patient__user__first_name__icontains=busqueda) |
            Q(patient__user__last_name__icontains=busqueda) |
            Q(doctor__user__first_name__icontains=busqueda) |
            Q(doctor__user__last_name__icontains=busqueda) |
            Q(doctor__specialty__name__icontains=busqueda)
        )
        
    citas = citas.order_by('date', 'time')
    
    paginador = Paginator(citas, 10)
    numero_pagina = request.GET.get('page')
    pagina_actual = paginador.get_page(numero_pagina)
    
    return render(request, 'appointments/appointment_list.html', {
        'page_obj': pagina_actual,
        'status_filter': filtro_estado,
        'query': busqueda
    })

@login_required
def appointment_create(request):
    # Verificar que el paciente tenga perfil antes de agendar
    if request.user.is_patient and not hasattr(request.user, 'patient_profile'):
        messages.error(request, "Debes completar tu perfil de paciente antes de agendar una cita.")
        return redirect('dashboard')
        
    if request.method == 'POST':
        formulario = AppointmentForm(request.POST, user=request.user)
        if formulario.is_valid():
            cita = formulario.save(commit=False)
            # Si es paciente, asignamos su perfil automáticamente
            if request.user.is_patient:
                cita.patient = request.user.patient_profile
                cita.status = 'PENDING'
                
            try:
                # Disparar la validación completa del modelo (colisiones, fechas pasadas, horarios)
                cita.full_clean()
                cita.save()
                messages.success(request, "Cita agendada exitosamente.")
                return redirect('appointment_list')
            except ValidationError as e:
                # Mapear errores del modelo de vuelta al formulario
                for campo, errores in e.message_dict.items():
                    for error in errores:
                        formulario.add_error(campo if campo != '__all__' else None, error)
                messages.error(request, "Error de validación. Por favor revisa los detalles ingresados.")
        else:
            messages.error(request, "El formulario contiene errores.")
    else:
        formulario = AppointmentForm(user=request.user)
        
    # Traer médicos activos para el filtro por especialidad
    from doctors.models import Doctor
    medicos_activos = Doctor.objects.filter(user__is_active=True).select_related('user', 'specialty')
    
    return render(request, 'appointments/appointment_form.html', {
        'form': formulario,
        'action': 'Agendar',
        'doctors': medicos_activos
    })

@login_required
@role_required('ADMIN')
def appointment_reschedule(request, pk):
    cita = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        formulario = AppointmentForm(request.POST, instance=cita)
        if formulario.is_valid():
            cita_reprogramada = formulario.save(commit=False)
            try:
                cita_reprogramada.full_clean()
                cita_reprogramada.save()
                messages.success(request, "Cita reprogramada exitosamente.")
                return redirect('appointment_list')
            except ValidationError as e:
                for campo, errores in e.message_dict.items():
                    for error in errores:
                        formulario.add_error(campo if campo != '__all__' else None, error)
                messages.error(request, "Error de validación al reprogramar.")
        else:
            messages.error(request, "Verifica los datos del formulario.")
    else:
        formulario = AppointmentForm(instance=cita)
        
    from doctors.models import Doctor
    medicos_activos = Doctor.objects.filter(user__is_active=True).select_related('user', 'specialty')
    
    return render(request, 'appointments/appointment_form.html', {
        'form': formulario,
        'action': 'Reprogramar',
        'doctors': medicos_activos
    })

@login_required
def appointment_cancel(request, pk):
    cita = get_object_or_404(Appointment, pk=pk)
    
    # Verificar que el usuario tenga permiso para cancelar esta cita
    if request.user.is_patient and cita.patient != request.user.patient_profile:
        messages.error(request, "No tienes permiso para cancelar esta cita.")
        return redirect('appointment_list')
    elif request.user.is_doctor and cita.doctor != request.user.doctor_profile:
        messages.error(request, "No tienes permiso para cancelar esta cita.")
        return redirect('appointment_list')
        
    if request.method == 'POST':
        cita.status = 'CANCELLED'
        cita.save()
        messages.success(request, f"Cita del {cita.date} cancelada con éxito.")
        return redirect('appointment_list')
        
    return render(request, 'appointments/appointment_confirm_cancel.html', {'appointment': cita})

@login_required
@role_required('DOCTOR')
def appointment_complete(request, pk):
    cita = get_object_or_404(Appointment, pk=pk, doctor=request.user.doctor_profile)
    
    if request.method == 'POST':
        cita.status = 'COMPLETED'
        cita.save()
        messages.success(request, "Cita marcada como completada. Registra los detalles clínicos a continuación.")
        # Redirigir a crear el registro médico del paciente
        return redirect('medical_record_create', patient_id=cita.patient.id)
        
    return redirect('appointment_list')
