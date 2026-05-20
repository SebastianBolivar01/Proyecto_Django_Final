from django.contrib import admin
from .models import Appointment

class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'date_time', 'status']
    list_filter = ['status', 'date_time', 'doctor']
    search_fields = ['patient__user__first_name', 'patient__user__last_name', 'doctor__user__first_name', 'doctor__user__last_name', 'reason']
    ordering = ['-date_time']

admin.site.register(Appointment, AppointmentAdmin)

