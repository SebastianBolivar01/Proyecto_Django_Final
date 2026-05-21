from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from utils.permissions import role_required
from .forms import PatientRegistrationForm
from .models import CustomUser
from django.db.models import Q
from django.core.paginator import Paginator

def landing_page(request):
    # Si el usuario ya inició sesión, enviarlo al dashboard
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def register_patient(request):
    # Evitar que usuarios logueados se registren de nuevo
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        formulario = PatientRegistrationForm(request.POST)
        if formulario.is_valid():
            usuario = formulario.save()
            messages.success(request, f"Registro exitoso. ¡Bienvenido, {usuario.first_name}!")
            login(request, usuario)
            return redirect('dashboard')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        formulario = PatientRegistrationForm()
        
    return render(request, 'users/register.html', {'form': formulario})


@login_required
@role_required('ADMIN')
def user_list(request):
    # Obtener el término de búsqueda de la URL
    busqueda = request.GET.get('q', '')
    usuarios = CustomUser.objects.all().order_by('-date_joined')
    
    if busqueda:
        usuarios = usuarios.filter(
            Q(username__icontains=busqueda) |
            Q(first_name__icontains=busqueda) |
            Q(last_name__icontains=busqueda) |
            Q(email__icontains=busqueda)
        )
        
    # Configurar la paginación a 10 usuarios por página
    paginador = Paginator(usuarios, 10)
    numero_pagina = request.GET.get('page')
    pagina_actual = paginador.get_page(numero_pagina)
    
    return render(request, 'users/user_list.html', {
        'page_obj': pagina_actual,
        'query': busqueda
    })


@login_required
@role_required('ADMIN')
def user_toggle_status(request, user_id):
    usuario_modificar = get_object_or_404(CustomUser, id=user_id)
    
    # Un admin no debería poder desactivarse a sí mismo
    if usuario_modificar == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta de administrador.")
        return redirect('user_list')
        
    # Cambiar el estado activo/inactivo
    usuario_modificar.is_active = not usuario_modificar.is_active
    usuario_modificar.save()
    
    estado_str = "activado" if usuario_modificar.is_active else "desactivado"
    messages.success(request, f"Usuario {usuario_modificar.username} ha sido {estado_str} exitosamente.")
    return redirect('user_list')


