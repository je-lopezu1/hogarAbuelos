from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ResidentForm
from residents.models import Resident
from residents.logic import residents_logic as rl

def residents_view(request):
    residents = rl.get_all_residents()
    return render(request, 'list_residents.html', {'residents': residents})

def create_resident_view(request):
    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['name']
            edad = form.cleaned_data['age']
            condicion = form.cleaned_data['medical_condition']
            medicamentos = form.cleaned_data['medications']
            rl.create_resident({'name': nombre, 'age': edad, 'medical_condition': condicion, 'medications': medicamentos})
            return redirect('residents:residents_view')
    else:
        form = ResidentForm()
    
    return render(request, 'create_resident.html', {'form': form})

def delete_resident_view(request, pk):
    if request.method == 'POST':
        resident = get_object_or_404(Resident, pk=pk)
        resident.delete()
        return redirect('residents:residents_view')
    return HttpResponse(status=405)

def update_resident_view(request, pk):
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            return redirect('residents:residents_view')
    else:
        form = ResidentForm(instance=resident)
    
    return render(request, 'update_resident.html', {'form': form})

def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)
    doses = rl.get_all_resident_medication_doses(resident)
    return render(request, 'list_doses.html', {'resident': resident, 'doses': doses})