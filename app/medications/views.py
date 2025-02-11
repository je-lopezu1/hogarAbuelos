from django.shortcuts import get_object_or_404, redirect, render

from .models import Medication
from .forms import MedicationForm
from medications.logic import medication_logic as ml
from django.core import serializers
from django.http import HttpResponse

# Create your views here.
def medications_view(request):
    if request.method == 'GET':
        medications = ml.get_all_medications()
        return render(request, 'list_medications.html', {'medications': medications})

def create_medication_view(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['name']
            ml.create_medication({'name': nombre})
            return redirect('medications:medications_view')
    else:
        form = MedicationForm()

    return render(request, 'create_medication.html', {'form': form})

def delete_medication_view(request, pk):
    if request.method == 'POST':
        medication = get_object_or_404(Medication, pk=pk)
        medication.delete()
        return redirect('medications:medications_view')
    return HttpResponse(status=405)

def update_medication_view(request, pk):
    medication = get_object_or_404(Medication, pk=pk)
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            form.save()
            return redirect('medications:medications_view')
    else:
        form = MedicationForm(instance=medication)

    return render(request, 'update_medication.html', {'form': form})