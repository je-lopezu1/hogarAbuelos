from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required # Import login_required

from medication_dose.models import MedicationDose
from medication_dose.forms import MedicationDoseForm, MedicationDoseUpdateForm
from residents.models import Resident
import medication_dose.logic.medication_dose_logic as mdl
from datetime import datetime
from authentication.models import UserProfile # Import UserProfile

@login_required
def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)

    # Basic authorization check: Ensure the user is allowed to view this resident's doses
    # Doctors and Administrators can view all. Family can view their related residents.
    try:
        user_profile = request.user.profile
        if user_profile.is_family() and resident not in user_profile.related_residents.all():
             messages.error(request, 'No tienes permiso para ver las dosis de este residente.')
             return redirect('dashboard:index') # Or redirect to the family dashboard

        # No explicit check needed for Doctor/Administrator as middleware handles it
        # And they have access to all residents in the view logic anyway.

    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('dashboard:index')


    doses = mdl.get_all_resident_medication_doses(resident).order_by('-day', '-time') # Ordering doses here
    return render(request, 'resident_doses.html', {'resident': resident, 'doses': doses})

@login_required # Require login
def create_medication_dose_view(request, resident_pk):
    # Access restricted to 'doctor' by middleware
    resident = get_object_or_404(Resident, pk=resident_pk)

    if request.method == 'POST':
        form = MedicationDoseForm(request.POST, resident=resident)  # Pass resident to form
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
            messages.success(request, 'Dosis agregada correctamente.')
            return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)
        else:
             messages.error(request, 'Error al agregar la dosis. Por favor, verifica los campos.')
    else:
        form = MedicationDoseForm(resident=resident)

    return render(request, 'create_dose.html', {'resident': resident, 'form': form})

@login_required # Require login
def delete_medication_dose_view(request, resident_pk, dose_pk):
    # Access restricted to 'doctor' by middleware
    dose = get_object_or_404(MedicationDose, pk=dose_pk)

    # Optional: Add an extra check to ensure the dose belongs to the resident_pk in the URL
    if dose.resident.pk != resident_pk:
         messages.error(request, 'La dosis no corresponde al residente indicado.')
         return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)

    if request.method == 'POST':
        mdl.delete_medication_dose(dose_pk)
        messages.success(request, 'Dosis eliminada correctamente.')
        return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)
    return HttpResponse(status=405) # Method Not Allowed for GET

@login_required # Require login
def update_medication_dose_view(request, resident_pk, dose_pk):
    # Access restricted to 'doctor' by middleware
    dose = get_object_or_404(MedicationDose, pk=dose_pk)
    resident = get_object_or_404(Resident, pk=resident_pk)

    # Verify that the dose belongs to the resident
    if dose.resident.pk != resident.pk:
        messages.error(request, 'La dosis no corresponde al residente seleccionado.')
        return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

    if request.method == 'POST':
        form = MedicationDoseUpdateForm(request.POST, instance=dose, resident=resident)
        if form.is_valid():
            mdl.update_medication_dose(dose_pk, form.cleaned_data)
            messages.success(request, 'Dosis actualizada correctamente.')
            return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)
        else:
            messages.error(request, 'Error al actualizar la dosis. Por favor, verifica los campos.')
    else:
        form = MedicationDoseUpdateForm(instance=dose, resident=resident)

    context = {
        'form': form,
        'dose': dose,
        'resident': resident,
    }
    return render(request, 'update_dose.html', context)