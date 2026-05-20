from django import forms
from .models import MedicalRecord

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['diagnosis', 'treatment', 'medications', 'notes']
        widgets = {
            'diagnosis': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Describe el diagnóstico clínico del paciente...'
            }),
            'treatment': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Describe el plan de tratamiento indicado...'
            }),
            'medications': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Lista los medicamentos prescritos (uno por línea)...'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 'rows': 3,
                'placeholder': 'Observaciones adicionales, notas de seguimiento...'
            }),
        }
        labels = {
            'diagnosis': 'Diagnóstico Clínico',
            'treatment': 'Plan de Tratamiento',
            'medications': 'Medicamentos Prescritos',
            'notes': 'Notas y Observaciones Adicionales',
        }
