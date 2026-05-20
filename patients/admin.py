from django.contrib import admin
from .models import Patient

class PatientAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'gender', 'blood_type', 'date_of_birth']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'blood_type']
    list_filter = ['gender', 'blood_type']

    def get_full_name(self, obj):
        return obj.user.get_full_name() or obj.user.username
    get_full_name.short_description = 'Paciente'

admin.site.register(Patient, PatientAdmin)

