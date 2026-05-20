from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db import transaction
from .models import CustomUser
from patients.models import Patient

class PatientRegistrationForm(forms.ModelForm):
    # CustomUser fields
    username = forms.CharField(max_length=150, label="Nombre de Usuario")
    email = forms.EmailField(label="Correo Electrónico")
    password = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
    first_name = forms.CharField(max_length=150, label="Nombres")
    last_name = forms.CharField(max_length=150, label="Apellidos")
    phone_number = forms.CharField(max_length=20, required=False, label="Teléfono")

    # Patient fields
    date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        label="Fecha de Nacimiento"
    )
    gender = forms.ChoiceField(choices=Patient.GENDER_CHOICES, label="Género")
    address = forms.CharField(max_length=255, required=False, label="Dirección")
    blood_type = forms.ChoiceField(choices=Patient.BLOOD_TYPES, label="Grupo Sanguíneo")
    emergency_contact_name = forms.CharField(max_length=100, required=False, label="Contacto de Emergencia (Nombre)")
    emergency_contact_phone = forms.CharField(max_length=20, required=False, label="Contacto de Emergencia (Teléfono)")

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.Select):
                field.widget.attrs.update({'class': 'form-select'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'PATIENT'
        user.set_password(self.cleaned_data['password'])
        
        if commit:
            with transaction.atomic():
                user.save()
                Patient.objects.create(
                    user=user,
                    date_of_birth=self.cleaned_data['date_of_birth'],
                    gender=self.cleaned_data['gender'],
                    address=self.cleaned_data['address'],
                    blood_type=self.cleaned_data['blood_type'],
                    emergency_contact_name=self.cleaned_data['emergency_contact_name'],
                    emergency_contact_phone=self.cleaned_data['emergency_contact_phone']
                )
        return user

