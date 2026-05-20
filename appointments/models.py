from django.db import models
from patients.models import Patient
from doctors.models import Doctor
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

class Appointment(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pendiente'),
        ('CONFIRMED', 'Confirmada'),
        ('CANCELLED', 'Cancelada'),
        ('COMPLETED', 'Completada'),
    )

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='appointments', verbose_name="Paciente")
    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name='appointments', verbose_name="Médico")
    date_time = models.DateTimeField(verbose_name="Fecha y Hora")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    reason = models.CharField(max_length=255, verbose_name="Motivo de la Consulta")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['date_time']

    def clean(self):
        # Prevent past dates for new/unsaved or rescheduled appointments
        if self.date_time:
            if not self.pk:
                if self.date_time < timezone.now():
                    raise ValidationError("La fecha y hora de la cita no puede estar en el pasado.")
            else:
                original = Appointment.objects.get(pk=self.pk)
                if original.date_time != self.date_time and self.date_time < timezone.now():
                    raise ValidationError("La fecha y hora de la cita no puede estar en el pasado.")
            
            # Prevent doctor overlap. Let's assume an appointment lasts 30 minutes.
            # So, check if there is another appointment for the same doctor within +/- 29 minutes.
            start_range = self.date_time - timedelta(minutes=29)
            end_range = self.date_time + timedelta(minutes=29)
            
            overlapping_appointments = Appointment.objects.filter(
                doctor=self.doctor,
                date_time__range=(start_range, end_range)
            ).exclude(status='CANCELLED')
            
            if self.pk:
                overlapping_appointments = overlapping_appointments.exclude(pk=self.pk)
                
            if overlapping_appointments.exists():
                raise ValidationError("El médico ya tiene otra cita programada en este rango de tiempo (las citas duran 30 minutos).")

            # Prevent patient overlap
            overlapping_patient_appointments = Appointment.objects.filter(
                patient=self.patient,
                date_time__range=(start_range, end_range)
            ).exclude(status='CANCELLED')
            
            if self.pk:
                overlapping_patient_appointments = overlapping_patient_appointments.exclude(pk=self.pk)
                
            if overlapping_patient_appointments.exists():
                raise ValidationError("El paciente ya tiene otra cita programada en este rango de tiempo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cita de {self.patient} con Dr. {self.doctor.user.last_name} - {self.date_time.strftime('%d/%m/%Y %H:%M')}"

