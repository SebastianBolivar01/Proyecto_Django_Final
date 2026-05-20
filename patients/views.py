from django.shortcuts import render, redirect

def patient_list(request):
    return render(request, 'patients/patient_list.html')

def patient_create(request):
    return redirect('patient_list')

def patient_update(request, pk):
    return redirect('patient_list')

def patient_delete(request, pk):
    return redirect('patient_list')

def patient_detail(request, pk):
    return render(request, 'patients/patient_detail.html')

