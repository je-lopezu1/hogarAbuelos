from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse

from medication_dose.forms import MedicationDoseForm
from residents.models import Resident
import medication_dose.logic.medication_dose_logic as mdl
from datetime import datetime

def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)
    doses = mdl.get_all_resident_medication_doses(resident)
    return render(request, 'list_doses.html', {'resident': resident, 'doses': doses})

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
