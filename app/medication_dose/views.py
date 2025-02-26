from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse

from residents.models import Resident
import medication_dose.logic.medication_dose_logic as mdl

def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)
    doses = mdl.get_all_resident_medication_doses(resident)
    return render(request, 'list_doses.html', {'resident': resident, 'doses': doses})

def create_dose_view(request):
    if request.method == 'POST':
        medication = request.POST['medication']

        dose = request.POST['dose']
        
        if not dose:
            return JsonResponse({"error": "La dosis es obligatoria"}, status=400)

        day = request.POST['day']
        mdl.create_medication_dose({'medication': medication, 'dose': dose, 'day': day})
        return redirect('medication_dose:doses_view')
    else:
        return render(request, 'create_dose.html')