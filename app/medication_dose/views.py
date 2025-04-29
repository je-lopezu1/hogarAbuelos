from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse

from medication_dose.models import MedicationDose
from medication_dose.forms import MedicationDoseForm
from medication_dose.forms import MedicationDoseUpdateForm
from residents.models import Resident
import medication_dose.logic.medication_dose_logic as mdl
from datetime import datetime

def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)
    doses = mdl.get_all_resident_medication_doses(resident).order_by('-day', '-time') # Ordering doses here
    return render(request, 'resident_doses.html', {'resident': resident, 'doses': doses})

def create_medication_dose_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)  # Obtener residente

    if request.method == 'POST':
        form = MedicationDoseForm(request.POST, resident=resident)  # Pasar residente al form
        if form.is_valid():
            medication = form.cleaned_data.get('medication')
            dose = form.cleaned_data.get('dose')
            day = datetime.today().date()
            time = datetime.today().time()
            medication_dose_data = {
                'resident': resident,
                'medication': medication,
                'dose': dose,
                'day': day,
                'time': time,
            }
            mdl.create_medication_dose(medication_dose_data)
            return redirect('residents:resident_doses_view', resident_pk=resident.pk)
    else:
        form = MedicationDoseForm(resident=resident)

    return render(request, 'create_dose.html', {'resident': resident, 'form': form})

def delete_medication_dose_view(request, resident_pk, dose_pk):
    if request.method == 'POST':
        mdl.delete_medication_dose(dose_pk)
        return redirect('residents:resident_doses_view', resident_pk=resident_pk)
    return HttpResponse(status=405)

def update_medication_dose_view(request, resident_pk, dose_pk):
    # Obtenemos tanto la dosis como el residente usando los parámetros recibidos
    dose = get_object_or_404(MedicationDose, pk=dose_pk)
    resident = get_object_or_404(Resident, pk=resident_pk)
    
    # Verificamos que la dosis corresponda al residente
    if dose.resident.pk != resident.pk:
        messages.error(request, 'La dosis no corresponde al residente seleccionado.')
        return redirect('residents:resident_doses_view', resident_pk=resident.pk)
    
    if request.method == 'POST':
        form = MedicationDoseUpdateForm(request.POST, instance=dose, resident=resident)
        if form.is_valid():
            mdl.update_medication_dose(dose_pk, form.cleaned_data)
            messages.success(request, 'Dosis actualizada correctamente.')
            return redirect('residents:resident_doses_view', resident_pk=resident.pk)
    else:
        form = MedicationDoseUpdateForm(instance=dose, resident=resident)
    
    context = {
        'form': form,
        'dose': dose,
        'resident': resident,
    }
    return render(request, 'update_dose.html', context)