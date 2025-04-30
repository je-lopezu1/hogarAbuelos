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
        ('administrator', 'Administrador'), # Changed from 'patient'
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

    # Fields specific to different user types
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

    # This field was for the patient role. Now it can be used optionally for admin to view a specific resident on their dashboard (though the dashboard logic doesn't currently use it this way). Keeping it here for form structure.
    # Filtering out residents already assigned to an administrator profile
    assigned_residents_admin = UserProfile.objects.filter(user_type='administrator', resident__isnull=False).values_list('resident_id', flat=True)

    resident = forms.ModelChoiceField(
        queryset=Resident.objects.exclude(id__in=assigned_residents_admin),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'resident-field' # Keep ID for JS logic
        })
    )


    # For other resident relationships (e.g., family)
    assigned_residents_family = UserProfile.objects.filter(user_type='family', related_residents__isnull=False).values_list('related_residents', flat=True)
    available_residents_for_family = Resident.objects.exclude(id__in=assigned_residents_admin) # Family can relate to residents not assigned to an admin


    related_residents = forms.ModelMultipleChoiceField(
        queryset=Resident.objects.filter(id__in=available_residents_for_family),
        required=False,
        widget=forms.SelectMultiple(attrs={
            'class': 'form-control',
            'id': 'related-residents-field' # Keep ID for JS logic
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
        resident_for_admin = cleaned_data.get("resident")
        related_residents_for_family = cleaned_data.get("related_residents")

        # Validation for Administrator role
        if user_type == 'administrator':
             # Optionally, if you want to associate an admin with ONE specific resident for their dashboard view (though the current dashboard doesn't use this), you could add a check here.
             # Example:
             # if resident_for_admin and UserProfile.objects.filter(user_type='administrator', resident=resident_for_admin).exclude(pk=self.instance.pk if self.instance else None).exists():
             #      self.add_error('resident', f'This resident is already assigned to another administrator profile.')
            pass # No specific resident required for admin in this logic

        # Validation for Family role
        if user_type == 'family':
            # Add validation if you require families to be related to at least one resident
            # Example:
            # if not related_residents_for_family:
            #     self.add_error('related_residents', 'Familiar users must be related to at least one resident.')
            pass # No specific resident validation required for family in this logic

        # Note: The original patient-specific validation is removed as there is no patient role now.

        return cleaned_data

    # Override save to handle profile creation/update correctly
    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()

            user_profile, created = UserProfile.objects.get_or_create(user=user)

            user_type = self.cleaned_data.get('user_type')
            user_profile.user_type = user_type
            user_profile.phone_number = self.cleaned_data.get('phone_number')

            # Clear previous role-specific fields
            user_profile.specialty = ''
            user_profile.relationship = ''
            user_profile.resident = None
            user_profile.related_residents.clear()


            if user_type == 'doctor':
                user_profile.specialty = self.cleaned_data.get('specialty')

            elif user_type == 'administrator':
                 # Optionally associate with one resident if needed for dashboard logic
                 user_profile.resident = self.cleaned_data.get('resident')

            elif user_type == 'family':
                user_profile.relationship = self.cleaned_data.get('relationship')
                user_profile.save() # Save before setting M2M
                user_profile.related_residents.set(self.cleaned_data.get('related_residents'))

            if user_type != 'family': # Only save here if not family (family saved earlier)
                 user_profile.save()

        return user