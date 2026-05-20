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
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'landing.html')


def register_patient(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        form = PatientRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, f"Registro exitoso. ¡Bienvenido, {user.first_name}!")
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, "Por favor, corrige los errores en el formulario.")
    else:
        form = PatientRegistrationForm()
        
    return render(request, 'users/register.html', {'form': form})


@login_required
@role_required('ADMIN')
def user_list(request):
    query = request.GET.get('q', '')
    users = CustomUser.objects.all().order_by('-date_joined')
    
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
        
    paginator = Paginator(users, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'users/user_list.html', {
        'page_obj': page_obj,
        'query': query
    })


@login_required
@role_required('ADMIN')
def user_toggle_status(request, user_id):
    user_to_toggle = get_object_or_404(CustomUser, id=user_id)
    
    if user_to_toggle == request.user:
        messages.error(request, "No puedes desactivar tu propia cuenta de administrador.")
        return redirect('user_list')
        
    user_to_toggle.is_active = not user_to_toggle.is_active
    user_to_toggle.save()
    
    status_str = "activado" if user_to_toggle.is_active else "desactivado"
    messages.success(request, f"Usuario {user_to_toggle.username} ha sido {status_str} exitosamente.")
    return redirect('user_list')


