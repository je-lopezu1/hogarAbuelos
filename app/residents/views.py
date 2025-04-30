from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required # Import login_required
from django.contrib import messages

from .forms import ResidentForm
from residents.models import Resident
from residents.logic import residents_logic as rl
from authentication.models import UserProfile # Import UserProfile
# Import the correct resident_doses_view from the medication_dose app
from medication_dose.views import resident_doses_view as medication_dose_resident_doses_view

@login_required # Require login
def residents_view(request):
    # Access restricted to 'doctor', 'administrator' by middleware
    residents = rl.get_all_residents()
    return render(request, 'list_residents.html', {'residents': residents})

@login_required # Require login
def create_resident_view(request):
    # Access restricted to 'administrator' by middleware
    if request.method == 'POST':
        form = ResidentForm(request.POST)
        if form.is_valid():
            resident_data = form.cleaned_data
            rl.create_resident(resident_data)
            messages.success(request, f'Residente "{resident_data["name"]}" creado correctamente.')
            return redirect('residents:residents_view')
        else:
             messages.error(request, 'Error al crear el residente. Por favor, verifica los campos.')
    else:
        form = ResidentForm()

    return render(request, 'create_resident.html', {'form': form})

@login_required # Require login
def delete_resident_view(request, pk):
    # Access restricted to 'administrator' by middleware
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        try:
            resident_name = resident.name # Get name before deleting
            resident.delete()
            messages.success(request, f'Residente "{resident_name}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el residente: {e}')

        return redirect('residents:residents_view')
    return HttpResponse(status=405) # Method Not Allowed for GET

@login_required # Require login
def update_resident_view(request, pk):
    # Access restricted to 'administrator' by middleware
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        if form.is_valid():
            form.save()
            messages.success(request, f'Residente "{resident.name}" actualizado correctamente.')
            return redirect('residents:residents_view')
        else:
            messages.error(request, 'Error al actualizar el residente. Por favor, verifica los campos.')
    else:
        form = ResidentForm(instance=resident)

    return render(request, 'update_resident.html', {'form': form})

# Use the resident_doses_view from the medication_dose app
resident_doses_view = medication_dose_resident_doses_view