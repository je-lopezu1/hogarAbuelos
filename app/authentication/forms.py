from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from residents.models import Resident

class UserLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Nombre de usuario'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'form-control',
        'placeholder': 'Contraseña'
    }))

class UserSignupForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Paciente'),
        ('family', 'Familiar')
    )
    
    first_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre'})
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apellidos'})
    )
    email = forms.EmailField(
        max_length=254, 
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    phone_number = forms.CharField(
        max_length=15, 
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Número telefónico'})
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Campos específicos para diferentes tipos de usuario
    specialty = forms.CharField(
        max_length=100, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Especialidad médica',
            'id': 'specialty-field'
        })
    )
    relationship = forms.CharField(
        max_length=50, 
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Relación con el residente',
            'id': 'relationship-field'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Filtrar residentes que ya están asignados a un usuario como paciente
        assigned_residents = UserProfile.objects.filter(resident__isnull=False).values_list('resident_id', flat=True)
        
        # Actualizar los querysets para los campos de residentes
        self.fields['resident'] = forms.ModelChoiceField(
            queryset=Resident.objects.exclude(id__in=assigned_residents),
            required=False,
            widget=forms.Select(attrs={
                'class': 'form-control',
                'id': 'resident-field'
            })
        )
        
        # Para los otros tipos de relaciones con residentes, mostramos todos
        self.fields['related_residents'] = forms.ModelMultipleChoiceField(
            queryset=Resident.objects.all(),
            required=False,
            widget=forms.SelectMultiple(attrs={
                'class': 'form-control',
                'id': 'related-residents-field'
            })
        )
        
        self.fields['patients'] = forms.ModelMultipleChoiceField(
            queryset=Resident.objects.all(),
            required=False,
            widget=forms.SelectMultiple(attrs={
                'class': 'form-control',
                'id': 'patients-field'
            })
        )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de usuario'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'}),
        }
        
    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get("user_type")
        resident = cleaned_data.get("resident")
        
        # Validar que un paciente tenga un residente seleccionado
        if user_type == 'patient' and not resident:
            self.add_error('resident', 'Para un usuario tipo Paciente, debe seleccionar un perfil de residente.')
            
        # Validar que el residente seleccionado no esté ya asignado
        if resident:
            if UserProfile.objects.filter(resident=resident).exists():
                self.add_error('resident', f'El residente {resident.name} ya está asignado a otro usuario.')
                
        return cleaned_data