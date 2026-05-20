from django import forms
from django.db import transaction
from .models import Doctor, Specialty
from users.models import CustomUser

class SpecialtyForm(forms.ModelForm):
    class Meta:
        model = Specialty
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la especialidad'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción de la especialidad'}),
        }
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
        }

class DoctorForm(forms.ModelForm):
    # CustomUser fields
    username = forms.CharField(max_length=150, label="Nombre de Usuario")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, required=False, label="Contraseña (dejar en blanco para no cambiar en edición)")
    first_name = forms.CharField(max_length=150, label="Nombres")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    phone_number = forms.CharField(max_length=20, required=False, label="Teléfono")

    is_active = forms.BooleanField(required=False, label="Habilitar cuenta del médico", initial=True)

    class Meta:
        model = Doctor
        fields = ['specialty', 'license_number']
        labels = {
            'specialty': 'Especialidad',
            'license_number': 'Número de Licencia',
        }

    def __init__(self, *args, **kwargs):
        self.instance_user = kwargs.pop('user_instance', None)
        super().__init__(*args, **kwargs)
        
        # Aplicar clases de Bootstrap
        for nombre_campo, campo in self.fields.items():
            if nombre_campo == 'is_active':
                campo.widget.attrs.update({'class': 'form-check-input'})
            elif isinstance(campo.widget, forms.Select):
                campo.widget.attrs.update({'class': 'form-select'})
            else:
                campo.widget.attrs.update({'class': 'form-control'})
                
        # Si estamos editando, rellenar campos de CustomUser
        if self.instance and self.instance.pk:
            usuario = self.instance.user
            self.fields['username'].initial = usuario.username
            self.fields['email'].initial = usuario.email
            self.fields['first_name'].initial = usuario.first_name
            self.fields['last_name'].initial = usuario.last_name
            self.fields['phone_number'].initial = usuario.phone_number
            # La contraseña no es obligatoria al editar
            self.fields['password'].required = False
        else:
            self.fields['password'].required = True

    def clean_username(self):
        nombre_usuario = self.cleaned_data.get('username')
        consulta = CustomUser.objects.filter(username=nombre_usuario)
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
        
        with transaction.atomic():
            if self.instance and self.instance.pk:
                # Actualizar usuario y perfil existentes
                usuario = self.instance.user
                usuario.username = datos_limpios['username']
                usuario.email = datos_limpios['email']
                usuario.first_name = datos_limpios['first_name']
                usuario.last_name = datos_limpios['last_name']
                usuario.phone_number = datos_limpios['phone_number']
                usuario.is_active = datos_limpios.get('is_active', True)
                
                contrasena = datos_limpios.get('password')
                if contrasena:
                    usuario.set_password(contrasena)
                usuario.save()
                
                medico = super().save(commit=False)
                medico.user = usuario
                if commit:
                    medico.save()
                return medico
            else:
                # Crear nuevo usuario y perfil
                usuario = CustomUser.objects.create(
                    username=datos_limpios['username'],
                    email=datos_limpios['email'],
                    first_name=datos_limpios['first_name'],
                    last_name=datos_limpios['last_name'],
                    phone_number=datos_limpios['phone_number'],
                    role='DOCTOR',
                    is_active=datos_limpios.get('is_active', True)
                )
                usuario.set_password(datos_limpios['password'])
                usuario.save()
                
                medico = super().save(commit=False)
                medico.user = usuario
                if commit:
                    medico.save()
                return medico
