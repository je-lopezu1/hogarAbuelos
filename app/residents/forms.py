from django import forms

from medications.models import Medication
from .models import Resident

class ResidentForm(forms.ModelForm):
    medications = forms.ModelMultipleChoiceField(
        queryset=Medication.objects.all(),
        widget=forms.CheckboxSelectMultiple,  # Usa checkboxes en lugar de select multiple
    )
    class Meta:
        model = Resident
        fields = ['name', 'age', 'medical_condition', 'medications']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del residente'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad del residente'}),
            'medical_condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Condición médica del residente'}),
            'medications': forms.SelectMultiple(attrs={'class': 'form-control'})
        }  