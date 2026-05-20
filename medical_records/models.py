from django.db import models
from patients.models import Patient
from doctors.models import Doctor

class MedicalRecord(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records', verbose_name="Paciente")
    doctor = models.ForeignKey(Doctor, on_delete=models.SET_NULL, null=True, related_name='medical_records', verbose_name="Médico Responsable")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")
    diagnosis = models.TextField(verbose_name="Diagnóstico")
    treatment = models.TextField(verbose_name="Tratamiento")
    medications = models.TextField(blank=True, null=True, verbose_name="Medicamentos Prescritos")
    notes = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales")

    class Meta:
        verbose_name = "Historia Clínica"
        verbose_name_plural = "Historias Clínicas"
        ordering = ['-created_at']

    def __str__(self):
        return f"Registro de {self.patient} - {self.created_at.strftime('%d/%m/%Y')} por Dr. {self.doctor.user.last_name if self.doctor else 'Desconocido'}"

