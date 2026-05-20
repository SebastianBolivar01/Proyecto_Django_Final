from django.shortcuts import render, redirect

def reports_home(request):
    return render(request, 'reports/home.html')

def export_appointments_excel(request):
    return redirect('reports_home')

def export_appointment_pdf(request, appointment_id):
    return redirect('reports_home')

def export_medical_record_pdf(request, record_id):
    return redirect('reports_home')

