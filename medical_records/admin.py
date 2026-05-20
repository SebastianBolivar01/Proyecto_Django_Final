from django.contrib import admin
from .models import MedicalRecord

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date', 'diagnosis']
    list_filter = ['date', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'diagnosis', 'symptoms']
    ordering = ['-date']

admin.site.register(MedicalRecord, MedicalRecordAdmin)

