from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from utils.permissions import role_required
from .models import Doctor, Specialty
from .forms import SpecialtyForm, DoctorForm

# ==========================================
# CRUD DE ESPECIALIDADES
# ==========================================

@login_required
@role_required('ADMIN')
def specialty_list(request):
    busqueda = request.GET.get('q', '')
    especialidades = Specialty.objects.all().order_by('name')
    
    if busqueda:
        especialidades = especialidades.filter(
            Q(name__icontains=busqueda) |
            Q(description__icontains=busqueda)
        )
        
    paginador = Paginator(especialidades, 10)
    numero_pagina = request.GET.get('page')
    pagina_actual = paginador.get_page(numero_pagina)
    
    return render(request, 'doctors/specialty_list.html', {
        'page_obj': pagina_actual,
        'query': busqueda
    })

@login_required
@role_required('ADMIN')
def specialty_create(request):
    if request.method == 'POST':
        formulario = SpecialtyForm(request.POST)
        if formulario.is_valid():
            especialidad = formulario.save()
            messages.success(request, f"Especialidad '{especialidad.name}' creada exitosamente.")
            return redirect('specialty_list')
        else:
            messages.error(request, "Error al crear la especialidad. Verifica los campos.")
    else:
        formulario = SpecialtyForm()
    return render(request, 'doctors/specialty_form.html', {'form': formulario, 'action': 'Crear'})

@login_required
@role_required('ADMIN')
def specialty_update(request, pk):
    especialidad = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        formulario = SpecialtyForm(request.POST, instance=especialidad)
        if formulario.is_valid():
            especialidad = formulario.save()
            messages.success(request, f"Especialidad '{especialidad.name}' actualizada exitosamente.")
            return redirect('specialty_list')
        else:
            messages.error(request, "Error al actualizar la especialidad. Verifica los campos.")
    else:
        formulario = SpecialtyForm(instance=especialidad)
    return render(request, 'doctors/specialty_form.html', {'form': formulario, 'action': 'Editar'})

@login_required
@role_required('ADMIN')
def specialty_delete(request, pk):
    especialidad = get_object_or_404(Specialty, pk=pk)
    if request.method == 'POST':
        nombre = especialidad.name
        especialidad.delete()
        messages.success(request, f"Especialidad '{nombre}' eliminada exitosamente.")
        return redirect('specialty_list')
    return render(request, 'doctors/specialty_confirm_delete.html', {'specialty': especialidad})


# ==========================================
# CRUD DE MÉDICOS
# ==========================================

@login_required
@role_required('ADMIN')
def doctor_list(request):
    busqueda = request.GET.get('q', '')
    medicos = Doctor.objects.select_related('user', 'specialty').all().order_by('user__last_name', 'user__first_name')
    
    if busqueda:
        medicos = medicos.filter(
            Q(user__first_name__icontains=busqueda) |
            Q(user__last_name__icontains=busqueda) |
            Q(specialty__name__icontains=busqueda) |
            Q(license_number__icontains=busqueda)
        )
        
    paginador = Paginator(medicos, 10)
    numero_pagina = request.GET.get('page')
    pagina_actual = paginador.get_page(numero_pagina)
    
    return render(request, 'doctors/doctor_list.html', {
        'page_obj': pagina_actual,
        'query': busqueda
    })

@login_required
@role_required('ADMIN')
def doctor_create(request):
    if request.method == 'POST':
        formulario = DoctorForm(request.POST)
        if formulario.is_valid():
            medico = formulario.save()
            messages.success(request, f"Médico '{medico.user.get_full_name()}' registrado exitosamente.")
            return redirect('doctor_list')
        else:
            messages.error(request, "Error al registrar el médico. Por favor corrige los errores.")
    else:
        formulario = DoctorForm()
    return render(request, 'doctors/doctor_form.html', {'form': formulario, 'action': 'Registrar'})

@login_required
@role_required('ADMIN')
def doctor_update(request, pk):
    medico = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        formulario = DoctorForm(request.POST, instance=medico)
        if formulario.is_valid():
            medico = formulario.save()
            messages.success(request, f"Datos del médico '{medico.user.get_full_name()}' actualizados con éxito.")
            return redirect('doctor_list')
        else:
            messages.error(request, "Error al actualizar los datos del médico.")
    else:
        formulario = DoctorForm(instance=medico)
    return render(request, 'doctors/doctor_form.html', {'form': formulario, 'action': 'Editar'})

@login_required
@role_required('ADMIN')
def doctor_delete(request, pk):
    medico = get_object_or_404(Doctor, pk=pk)
    if request.method == 'POST':
        nombre_completo = medico.user.get_full_name()
        # Eliminar perfil y usuario asociado
        usuario = medico.user
        medico.delete()
        usuario.delete()
        messages.success(request, f"Médico '{nombre_completo}' y su usuario asociado han sido eliminados.")
        return redirect('doctor_list')
    return render(request, 'doctors/doctor_confirm_delete.html', {'doctor': medico})
