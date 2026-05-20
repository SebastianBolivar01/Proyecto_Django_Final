from django.contrib import admin
from .models import Specialty, Doctor

class SpecialtyAdmin(admin.ModelAdmin):
    list_display = ['name', 'description']
    search_fields = ['name']

class DoctorAdmin(admin.ModelAdmin):
    list_display = ['get_full_name', 'specialty', 'license_number', 'consulting_room']
    search_fields = ['user__first_name', 'user__last_name', 'user__username', 'license_number']
    list_filter = ['specialty']

    def get_full_name(self, obj):
        return f"Dr. {obj.user.get_full_name() or obj.user.username}"
    get_full_name.short_description = 'Médico'

admin.site.register(Specialty, SpecialtyAdmin)
admin.site.register(Doctor, DoctorAdmin)

