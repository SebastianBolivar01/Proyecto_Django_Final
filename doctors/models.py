from django.db import models
from django.conf import settings

class Specialty(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Especialidad")
    description = models.TextField(blank=True, null=True, verbose_name="Descripción")

    class Meta:
        verbose_name = "Especialidad"
        verbose_name_plural = "Especialidades"

    def __str__(self):
        return self.name


class Doctor(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='doctor_profile',
        verbose_name="Usuario"
    )
    specialty = models.ForeignKey(
        Specialty,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='doctors',
        verbose_name="Especialidad"
    )
    license_number = models.CharField(max_length=50, unique=True, verbose_name="Número de Licencia / Tarjeta Profesional")
    consulting_room = models.CharField(max_length=50, blank=True, null=True, verbose_name="Consultorio")
    bio = models.TextField(blank=True, null=True, verbose_name="Biografía / Notas")

    class Meta:
        verbose_name = "Médico"
        verbose_name_plural = "Médicos"

    def __str__(self):
        specialty_name = self.specialty.name if self.specialty else "Sin especialidad"
        return f"Dr. {self.user.get_full_name() or self.user.username} - {specialty_name}"

