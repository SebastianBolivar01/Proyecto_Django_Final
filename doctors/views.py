from django.shortcuts import render, redirect

# Doctor Views
def doctor_list(request):
    return render(request, 'doctors/doctor_list.html')

def doctor_create(request):
    return redirect('doctor_list')

def doctor_update(request, pk):
    return redirect('doctor_list')

def doctor_delete(request, pk):
    return redirect('doctor_list')

# Specialty Views
def specialty_list(request):
    return render(request, 'doctors/specialty_list.html')

def specialty_create(request):
    return redirect('specialty_list')

def specialty_update(request, pk):
    return redirect('specialty_list')

def specialty_delete(request, pk):
    return redirect('specialty_list')

