from django import forms

from medications.models import Medication
from .models import Resident, ResidentMedication

class ResidentForm(forms.ModelForm):
    # Keep the ManyToManyField for selecting medications, but quantity is handled separately
    medications = forms.ModelMultipleChoiceField(
        queryset=Medication.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False # Make it optional if a resident might not have medications initially
    )
    class Meta:
        model = Resident
        fields = ['name', 'age', 'medical_condition', 'medications']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del residente'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Edad del residente'}),
            'medical_condition': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Condición médica del residente'}),
            # medications widget is defined above
        }

# Form for managing resident medication quantities in the formset
class ResidentMedicationForm(forms.ModelForm):
    class Meta:
        model = ResidentMedication
        fields = ['quantity_on_hand']
        widgets = {
            'quantity_on_hand': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.medication:
            self.fields['quantity_on_hand'].label = f"{self.instance.medication.name} Cantidad:"

# New form for adding quantity to an existing ResidentMedication entry
class AddResidentMedicationQuantityForm(forms.Form):
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.none(), # Will be filtered in the view
        label="Medicamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    quantity_to_add = forms.IntegerField(
        label="Cantidad a Añadir",
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '1'})
    )

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)
        if resident:
            # Filter medications to only those currently assigned to the resident
            assigned_medication_ids = ResidentMedication.objects.filter(resident=resident).values_list('medication__id', flat=True)
            self.fields['medication'].queryset = Medication.objects.filter(id__in=assigned_medication_ids)