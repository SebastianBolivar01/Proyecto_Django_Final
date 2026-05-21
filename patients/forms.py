from django import forms
from django.db import transaction
from .models import Patient
from users.models import CustomUser

class PatientForm(forms.ModelForm):
    # CustomUser fields
    username = forms.CharField(max_length=150, label="Nombre de Usuario")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Contraseña (dejar en blanco para no cambiar en edición)")
    first_name = forms.CharField(max_length=150, label="Nombres")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    phone_number = forms.CharField(max_length=20, required=False, label="Teléfono")

    class Meta:
        model = Patient
        fields = [
            'date_of_birth', 'gender', 'address', 'blood_type', 
            'emergency_contact_name', 'emergency_contact_phone'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'date_of_birth': 'Fecha de Nacimiento',
            'gender': 'Género',
            'address': 'Dirección',
            'blood_type': 'Grupo Sanguíneo',
            'emergency_contact_name': 'Contacto de Emergencia (Nombre)',
            'emergency_contact_phone': 'Contacto de Emergencia (Teléfono)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases de Bootstrap a todos los campos
        for nombre_campo, campo in self.fields.items():
            if isinstance(campo.widget, forms.Select):
                campo.widget.attrs.update({'class': 'form-select'})
            else:
                campo.widget.attrs.update({'class': 'form-control'})
                
        # Si estamos editando, rellenar los datos del CustomUser
        if self.instance and self.instance.pk:
            usuario = self.instance.user
            self.fields['username'].initial = usuario.username
            self.fields['email'].initial = usuario.email
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['phone_number'].initial = usuario.phone_number
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def clean_username(self):
        nombre_usuario = self.cleaned_data.get('username')
        consulta = CustomUser.objects.filter(username=nombre_usuario)
        
        # Si estamos editando, excluir al usuario actual de la búsqueda
        if self.instance and self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.user.pk)
            
        if consulta.exists():
            raise forms.ValidationError("Este nombre de usuario ya está registrado.")
        return nombre_usuario

    def clean_email(self):
        correo = self.cleaned_data.get('email')
        consulta = CustomUser.objects.filter(email=correo)
        
        if self.instance and self.instance.pk:
            consulta = consulta.exclude(pk=self.instance.user.pk)
            
        if consulta.exists():
            raise forms.ValidationError("Este correo electrónico ya está registrado.")
        return correo

    def save(self, commit=True):
        datos_limpios = self.cleaned_data
        
        # Usar una transacción para asegurar que ambos modelos se guarden juntos o ninguno
        with transaction.atomic():
            if self.instance and self.instance.pk:
                # Actualizar usuario existente
                usuario = self.instance.user
                usuario.username = datos_limpios['username']
                usuario.email = datos_limpios['email']
                usuario.first_name = datos_limpios['first_name']
                usuario.last_name = datos_limpios['last_name']
                usuario.phone_number = datos_limpios['phone_number']
                
                contrasena = datos_limpios.get('password')
                if contrasena:
                    usuario.set_password(contrasena)
                usuario.save()
                
                paciente = super().save(commit=False)
                paciente.user = usuario
                if commit:
                    paciente.save()
                return paciente
            else:
                # Crear nuevo usuario y perfil
                usuario = CustomUser.objects.create(
                    username=datos_limpios['username'],
                    email=datos_limpios['email'],
                    first_name=datos_limpios['first_name'],
                    last_name=datos_limpios['last_name'],
                    phone_number=datos_limpios['phone_number'],
                    role='PATIENT'
                )
                usuario.set_password(datos_limpios['password'])
                usuario.save()
                
                paciente = super().save(commit=False)
                paciente.user = usuario
                if commit:
                    paciente.save()
                return paciente
