from django import forms
from .models import MedicationDose, Medication

class MedicationDoseForm(forms.ModelForm):
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.none(),  # Se filtrará en la vista
        label="Medicamento",
        empty_label="Seleccione un medicamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dose = forms.CharField(
        max_length=100,
        label="Dosis Administrada (Texto)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 5ml, 1 tableta'})
    )
    quantity_administered = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Cantidad Administrada",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01'})
    )

    class Meta:
        model = MedicationDose
        fields = ['medication', 'dose', 'quantity_administered']

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)
        if resident:
            self.fields['medication'].queryset = resident.medications.all()

class MedicationDoseUpdateForm(forms.ModelForm):
    medication = forms.ModelChoiceField(
        queryset=Medication.objects.none(),  # Se filtrará en la vista
        label="Medicamento",
        empty_label="Seleccione un medicamento",
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    dose = forms.CharField(
        max_length=100,
        label="Dosis Administrada (Texto)",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 5ml, 1 tableta'})
    )
    quantity_administered = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        label="Cantidad Administrada",
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01'})
    )

    class Meta:
        model = MedicationDose
        fields = ['medication', 'dose', 'quantity_administered']  # Permitimos editar ambos campos

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)

        # If we are editing an existing instance, get the original quantity
        self._original_quantity_administered = None
        if kwargs.get('instance'):
             self._original_quantity_administered = kwargs['instance'].quantity_administered

        # If a resident is provided, filter available medications
        if resident:
            self.fields['medication'].queryset = resident.medications.all()
        # If we are editing an existing instance and no resident was provided
        elif kwargs.get('instance') and not resident:
            instance = kwargs.get('instance')
            resident = instance.resident
            if resident:
                self.fields['medication'].queryset = resident.medications.all()

    def save(self, commit=True):
        dose_instance = super().save(commit=False)

        # Calculate the difference in quantity
        quantity_difference = self._original_quantity_administered - dose_instance.quantity_administered

        if commit:
            dose_instance.save()

            # Update inventory if the quantity changed
            if quantity_difference != 0:
                try:
                    inventory = dose_instance.medication.inventory
                    inventory.quantity += quantity_difference # Add back the original quantity, then subtract the new one
                    inventory.save()
                except MedicationInventory.DoesNotExist:
                     print(f"Warning: Inventory not found for medication {dose_instance.medication.name}. Inventory not updated on edit.")


        return dose_instance