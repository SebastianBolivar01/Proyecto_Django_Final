from django.contrib import admin
from .models import MedicalRecord

class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'created_at', 'diagnosis']
    list_filter = ['created_at', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'diagnosis']
    ordering = ['-created_at']

admin.site.register(MedicalRecord, MedicalRecordAdmin)

