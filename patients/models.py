from django.db import models
from django.conf import settings

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    )
    
    BLOOD_TYPES = (
        ('A+', 'A+'),
        ('A-', 'A-'),
        ('B+', 'B+'),
        ('B-', 'B-'),
        ('AB+', 'AB+'),
        ('AB-', 'AB-'),
        ('O+', 'O+'),
        ('O-', 'O-'),
    )

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='patient_profile',
        verbose_name="Usuario"
    )
    date_of_birth = models.DateField(verbose_name="Fecha de Nacimiento")
    gender = models.CharField(max_length=2, choices=GENDER_CHOICES, verbose_name="Género")
    address = models.CharField(max_length=255, blank=True, null=True, verbose_name="Dirección")
    blood_type = models.CharField(max_length=5, choices=BLOOD_TYPES, verbose_name="Grupo Sanguíneo")
    emergency_contact_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="Contacto de Emergencia (Nombre)")
    emergency_contact_phone = models.CharField(max_length=20, blank=True, null=True, verbose_name="Contacto de Emergencia (Teléfono)")

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"

    def __str__(self):
        return self.user.get_full_name() or self.user.username

