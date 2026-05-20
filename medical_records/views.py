from django.shortcuts import render, redirect

def medical_record_list(request):
    return render(request, 'medical_records/medical_record_list.html')

def medical_record_create(request, patient_id):
    return redirect('medical_record_list')

def medical_record_update(request, pk):
    return redirect('medical_record_list')

def medical_record_detail(request, pk):
    return render(request, 'medical_records/medical_record_detail.html')

