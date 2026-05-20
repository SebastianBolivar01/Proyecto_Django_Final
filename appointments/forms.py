from django import forms
from django.core.exceptions import ValidationError
from .models import Appointment
from doctors.models import Doctor, Specialty
from patients.models import Patient

class AppointmentForm(forms.ModelForm):
    specialty = forms.ModelChoiceField(
        queryset=Specialty.objects.all(),
        required=False,
        label="Especialidad",
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'date', 'time', 'status', 'reason']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'reason': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Motivo de la consulta...'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }
        labels = {
            'patient': 'Paciente',
            'doctor': 'Médico Especialista',
            'date': 'Fecha',
            'time': 'Hora',
            'status': 'Estado de la Cita',
            'reason': 'Motivo',
        }

    def __init__(self, *args, **kwargs):
        usuario = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Solo mostrar médicos activos en el desplegable
        self.fields['doctor'].queryset = Doctor.objects.filter(is_active=True).select_related('user', 'specialty')
        
        # Ajustar los campos según el rol del usuario
        if usuario:
            if usuario.is_patient:
                # Los pacientes no eligen su propio perfil ni el estado
                self.fields.pop('patient')
                self.fields.pop('status')
            elif usuario.is_admin:
                # El admin ve todo, solo formateamos los widgets
                self.fields['patient'].widget.attrs.update({'class': 'form-select'})
                self.fields['doctor'].widget.attrs.update({'class': 'form-select'})
                
        # Formatear las opciones del médico para que incluyan la especialidad
        opciones = [('', '---------')]
        for medico in self.fields['doctor'].queryset:
            opciones.append((medico.id, f"Dr. {medico.user.get_full_name()} ({medico.specialty.name})"))
        self.fields['doctor'].choices = opciones

    def clean(self):
        datos_limpios = super().clean()
        # La validación principal está en el método clean() del modelo.
        # Si 'patient' fue removido (rol Paciente), se asigna en la vista
        # y se dispara la validación completa con full_clean() desde ahí.
        return cleaned_data
