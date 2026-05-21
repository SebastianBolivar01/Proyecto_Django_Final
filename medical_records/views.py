from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from utils.permissions import role_required
from .models import MedicalRecord
from .forms import MedicalRecordForm
from patients.models import Patient


@login_required
def medical_record_list(request):
    # Filtrar registros según el rol
    if request.user.is_admin:
        registros = MedicalRecord.objects.select_related(
            'patient__user', 'doctor__user', 'doctor__specialty'
        ).all()
    elif request.user.is_doctor:
        registros = MedicalRecord.objects.filter(
            doctor=request.user.doctor_profile
        ).select_related('patient__user', 'doctor__user', 'doctor__specialty')
    elif request.user.is_patient:
        registros = MedicalRecord.objects.filter(
            patient=request.user.patient_profile
        ).select_related('patient__user', 'doctor__user', 'doctor__specialty')
    else:
        messages.error(request, "Acceso no autorizado.")
        return redirect('dashboard')

    busqueda = request.GET.get('q', '')
    if busqueda:
        registros = registros.filter(
            Q(patient__user__first_name__icontains=busqueda) |
            Q(patient__user__last_name__icontains=busqueda) |
            Q(diagnosis__icontains=busqueda) |
            Q(doctor__user__last_name__icontains=busqueda)
        )

    registros = registros.order_by('-created_at')
    paginador = Paginator(registros, 10)
    pagina_actual = paginador.get_page(request.GET.get('page'))

    return render(request, 'medical_records/medical_record_list.html', {
        'page_obj': pagina_actual,
        'query': busqueda,
    })


@login_required
@role_required('DOCTOR')
def medical_record_create(request, patient_id):
    paciente = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        formulario = MedicalRecordForm(request.POST)
        if formulario.is_valid():
            registro = formulario.save(commit=False)
            registro.patient = paciente
            registro.doctor = request.user.doctor_profile
            registro.save()
            messages.success(request, f"Registro clínico creado para {paciente.user.get_full_name()}.")
            return redirect('patient_detail', pk=paciente.id)
        else:
            messages.error(request, "Error al guardar el registro. Verifica los campos.")
    else:
        formulario = MedicalRecordForm()

    return render(request, 'medical_records/medical_record_form.html', {
        'form': formulario,
        'patient': paciente,
        'action': 'Crear',
    })


@login_required
@role_required('DOCTOR')
def medical_record_update(request, pk):
    registro = get_object_or_404(MedicalRecord, pk=pk, doctor=request.user.doctor_profile)

    if request.method == 'POST':
        formulario = MedicalRecordForm(request.POST, instance=registro)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Registro clínico actualizado correctamente.")
            return redirect('patient_detail', pk=registro.patient.id)
        else:
            messages.error(request, "Error al actualizar el registro.")
    else:
        formulario = MedicalRecordForm(instance=registro)

    return render(request, 'medical_records/medical_record_form.html', {
        'form': formulario,
        'patient': registro.patient,
        'action': 'Editar',
    })


@login_required
def medical_record_detail(request, pk):
    registro = get_object_or_404(MedicalRecord, pk=pk)

    # Los pacientes solo pueden ver sus propios registros
    if request.user.is_patient and registro.patient != request.user.patient_profile:
        messages.error(request, "No tienes acceso a este registro.")
        return redirect('dashboard')

    return render(request, 'medical_records/medical_record_detail.html', {'record': registro})
