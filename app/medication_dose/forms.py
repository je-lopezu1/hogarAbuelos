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
        label="Dosis Administrada",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. 5ml, 1 tableta'})
    )

    class Meta:
        model = MedicationDose
        fields = ['medication', 'dose']

    def __init__(self, *args, resident=None, **kwargs):
        super().__init__(*args, **kwargs)
        if resident:
            self.fields['medication'].queryset = resident.medications.all()
