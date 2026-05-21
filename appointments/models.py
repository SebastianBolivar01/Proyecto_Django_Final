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
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='PENDING', verbose_name="Estado")
    reason = models.CharField(max_length=255, verbose_name="Motivo de la Consulta")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    class Meta:
        verbose_name = "Cita Médica"
        verbose_name_plural = "Citas Médicas"
        ordering = ['date', 'time']

    def clean(self):
        from datetime import datetime
        # Evitar que se agenden citas en fechas pasadas
        if self.date and self.time:
            fecha_hora = timezone.make_aware(datetime.combine(self.date, self.time))
            
            if not self.pk:
                # Es una cita nueva: no puede estar en el pasado
                if fecha_hora < timezone.now():
                    raise ValidationError("La fecha y hora de la cita no puede estar en el pasado.")
            else:
                # Es una reprogramación: solo validar si la fecha u hora cambiaron
                cita_original = Appointment.objects.get(pk=self.pk)
                fecha_hora_original = timezone.make_aware(datetime.combine(cita_original.date, cita_original.time))
                if (cita_original.date != self.date or cita_original.time != self.time) and fecha_hora < timezone.now():
                    raise ValidationError("La fecha y hora de la cita no puede estar en el pasado.")
            
            # Verificar que el médico no tenga otra cita en el mismo rango de 30 min
            rango_inicio = fecha_hora - timedelta(minutes=29)
            rango_fin = fecha_hora + timedelta(minutes=29)
            
            citas_medico = Appointment.objects.filter(
                doctor=self.doctor,
                date=self.date
            ).exclude(status='CANCELLED')
            
            hay_conflicto = False
            for cita in citas_medico:
                if self.pk and cita.pk == self.pk:
                    continue  # Excluir la cita actual al editar
                cita_dt = timezone.make_aware(datetime.combine(cita.date, cita.time))
                if rango_inicio <= cita_dt <= rango_fin:
                    hay_conflicto = True
                    break
            
            if hay_conflicto:
                raise ValidationError("El médico ya tiene otra cita programada en este rango de tiempo (las citas duran 30 minutos).")

            # Verificar que el paciente no tenga otra cita al mismo tiempo
            citas_paciente = Appointment.objects.filter(
                patient=self.patient,
                date=self.date
            ).exclude(status='CANCELLED')
            
            conflicto_paciente = False
            for cita in citas_paciente:
                if self.pk and cita.pk == self.pk:
                    continue
                cita_dt = timezone.make_aware(datetime.combine(cita.date, cita.time))
                if rango_inicio <= cita_dt <= rango_fin:
                    conflicto_paciente = True
                    break
                    
            if conflicto_paciente:
                raise ValidationError("El paciente ya tiene otra cita programada en este rango de tiempo.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cita de {self.patient} con Dr. {self.doctor.user.last_name} - {self.date.strftime('%d/%m/%Y')} {self.time.strftime('%H:%M')}"

