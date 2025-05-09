from django import forms
from .models import Supply

class SupplyForm(forms.ModelForm):
    class Meta:
        model = Supply
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del insumo'})
        }