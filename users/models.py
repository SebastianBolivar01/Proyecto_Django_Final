from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrador'),
        ('DOCTOR', 'Médico'),
        ('PATIENT', 'Paciente'),
    )
    
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='PATIENT',
        verbose_name='Rol'
    )
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name='Teléfono'
    )
    
    @property
    def is_admin(self):
        return self.role == 'ADMIN' or self.is_superuser
        
    @property
    def is_doctor(self):
        return self.role == 'DOCTOR'
        
    @property
    def is_patient(self):
        return self.role == 'PATIENT'
        
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

