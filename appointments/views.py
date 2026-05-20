from django.shortcuts import render, redirect

def appointment_list(request):
    return render(request, 'appointments/appointment_list.html')

def appointment_create(request):
    return redirect('appointment_list')

def appointment_reschedule(request, pk):
    return redirect('appointment_list')

def appointment_cancel(request, pk):
    return redirect('appointment_list')

def appointment_complete(request, pk):
    return redirect('appointment_list')

