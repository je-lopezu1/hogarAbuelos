from django import forms
from .models import MedicationDose, Medication
from residents.models import ResidentMedication # Import ResidentMedication

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
        label="Cantidad a Administrar", # Clarified label
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01'})
    )

    class Meta:
        model = MedicationDose
        fields = ['medication', 'dose', 'quantity_administered']

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)
        if resident:
            # Filter medications to only those the resident is assigned (from ResidentMedication)
            assigned_medication_ids = ResidentMedication.objects.filter(resident=resident).values_list('medication__id', flat=True)
            self.fields['medication'].queryset = Medication.objects.filter(id__in=assigned_medication_ids)


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
        label="Cantidad a Administrar", # Clarified label
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01'})
    )

    class Meta:
        model = MedicationDose
        fields = ['medication', 'dose', 'quantity_administered']

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)

        # If we are editing an existing instance, store the original quantity and medication
        self._original_quantity_administered = None
        self._original_medication = None
        if kwargs.get('instance'):
             self._original_quantity_administered = kwargs['instance'].quantity_administered
             self._original_medication = kwargs['instance'].medication

        # Filter medications to only those the resident is assigned
        if resident:
            assigned_medication_ids = ResidentMedication.objects.filter(resident=resident).values_list('medication__id', flat=True)
            self.fields['medication'].queryset = Medication.objects.filter(id__in=assigned_medication_ids)
        # If editing an instance without resident provided, use the instance's resident
        elif kwargs.get('instance'):
            resident = kwargs['instance'].resident
            assigned_medication_ids = ResidentMedication.objects.filter(resident=resident).values_list('medication__id', flat=True)
            self.fields['medication'].queryset = Medication.objects.filter(id__in=assigned_medication_ids)


    def save(self, commit=True):
        dose_instance = super().save(commit=False)

        if commit:
            # Handle quantity adjustment based on changes BEFORE saving the dose
            new_medication = self.cleaned_data.get('medication') # Use cleaned_data for form data
            new_quantity = self.cleaned_data.get('quantity_administered')

            # If medication changed or quantity changed
            if self._original_medication != new_medication or self._original_quantity_administered != new_quantity:
                # Use atomic transaction in the view for safety

                # 1. Restore quantity to the original medication (if it existed)
                if self._original_medication and self._original_quantity_administered is not None:
                    try:
                        original_resident_medication = ResidentMedication.objects.get(
                            resident=dose_instance.resident,
                            medication=self._original_medication
                        )
                        original_resident_medication.quantity_on_hand += self._original_quantity_administered
                        original_resident_medication.save()
                    except ResidentMedication.DoesNotExist:
                        print(f"Warning: Original ResidentMedication not found for {dose_instance.resident.name} and {self._original_medication.name}. Quantity not restored on edit.")

                # 2. Deduct quantity from the new medication (if it exists)
                if new_medication and new_quantity is not None:
                    try:
                        new_resident_medication = ResidentMedication.objects.get(
                            resident=dose_instance.resident,
                            medication=new_medication
                        )
                         # The check for sufficient quantity is done in the view
                        new_resident_medication.quantity_on_hand -= new_quantity
                        new_resident_medication.save()

                    except ResidentMedication.DoesNotExist:
                        print(f"Warning: New ResidentMedication not found for {dose_instance.resident.name} and {new_medication.name}. Dose updated but quantity not updated.")


            dose_instance.save() # Save the dose instance AFTER quantity adjustments

        return dose_instance