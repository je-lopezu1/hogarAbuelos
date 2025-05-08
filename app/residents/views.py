from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction # Import transaction for atomic updates

from .forms import ResidentForm, ResidentMedicationForm
from residents.models import Resident, ResidentMedication
from residents.logic import residents_logic as rl
from authentication.models import UserProfile
from medication_dose.views import resident_doses_view as medication_dose_resident_doses_view
from medications.models import Medication

@login_required
def residents_view(request):
    # Access restricted to 'doctor', 'administrator' by middleware
    residents = rl.get_all_residents()
    # Prefetch related ResidentMedication objects for efficient access in the template
    residents = residents.prefetch_related('residentmedication_set__medication')

    return render(request, 'list_residents.html', {'residents': residents})

@login_required
def create_resident_view(request):
    # Access restricted to 'administrator' by middleware

    if request.method == 'POST':
        form = ResidentForm(request.POST)
        # Manually process medication quantities from POST data
        selected_medication_ids = request.POST.getlist('medications')
        initial_quantities = {}
        quantity_errors = False
        for med_id in selected_medication_ids:
             # Get the quantity for this medication from the form data
             quantity_str = request.POST.get(f'initial_quantity_{med_id}', '0')
             try:
                  quantity = int(quantity_str)
                  if quantity < 0:
                      messages.error(request, f"La cantidad inicial para el medicamento con ID {med_id} no puede ser negativa.")
                      quantity_errors = True
                  initial_quantities[int(med_id)] = quantity
             except ValueError:
                  messages.error(request, f"La cantidad inicial para el medicamento con ID {med_id} no es un número válido.")
                  quantity_errors = True

        # If there were quantity errors, re-render the form with errors
        if quantity_errors:
            # Need to reconstruct the form to show previously selected medications
            form = ResidentForm(request.POST) # Re-bind the form
            all_medications = Medication.objects.all() # Get all medications for checklist
            return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications})


        if form.is_valid() and not quantity_errors: # Ensure no quantity errors
            try:
                with transaction.atomic():
                    resident = form.save(commit=False)
                    resident.save() # Save the resident first to get a primary key

                    # Create ResidentMedication entries with initial quantities
                    for med_id, quantity in initial_quantities.items():
                         medication = get_object_or_404(Medication, pk=med_id)
                         ResidentMedication.objects.create(
                             resident=resident,
                             medication=medication,
                             quantity_on_hand=quantity
                         )

                    messages.success(request, f'Residente "{resident.name}" creado correctamente con medicamentos asignados.')
                    return redirect('residents:residents_view')

            except Exception as e:
                messages.error(request, f'Error al crear el residente o asignar medicamentos: {e}')
                # The atomic block will roll back if an error occurs
                # If resident was created before the error, it will be rolled back
                return render(request, 'create_resident.html', {'form': form, 'all_medications': Medication.objects.all()})

        else:
             messages.error(request, 'Error al crear el residente. Por favor, verifica los campos.')

    else:
        form = ResidentForm()

    # Pass all medications to the template for the medication selection checklist
    all_medications = Medication.objects.all()

    return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications})


@login_required
def delete_resident_view(request, pk):
    # Access restricted to 'administrator' by middleware
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        try:
            resident_name = resident.name
            # Deleting the resident will cascade delete related ResidentMedication and MedicationDose objects
            # No need to manually restore quantities here as the resident is gone.
            resident.delete()
            messages.success(request, f'Residente "{resident_name}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el residente: {e}')

        return redirect('residents:residents_view')
    return HttpResponse(status=405)

@login_required
def update_resident_view(request, pk):
    # Access restricted to 'administrator' by middleware
    resident = get_object_or_404(Resident, pk=pk)
    # Create an inline formset for managing ResidentMedication instances
    ResidentMedicationFormSet = inlineformset_factory(
        Resident,
        ResidentMedication,
        form=ResidentMedicationForm,
        fields=['medication', 'quantity_on_hand'],
        extra=1, # Allow adding one extra new medication row
        can_delete=True, # Allow removing medication rows
        widgets={
             # Use a Select widget for the medication field in the formset (only for new rows)
             'medication': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
    )


    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        formset = ResidentMedicationFormSet(request.POST, instance=resident)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save() # Save resident info

                    # Save the formset, handling creation, update, and deletion of ResidentMedication objects
                    formset.save()

                    messages.success(request, f'Residente "{resident.name}" actualizado correctamente.')
                    return redirect('residents:residents_view')

            except Exception as e:
                messages.error(request, f'Error al actualizar el residente o sus medicamentos: {e}')
                # The atomic block will roll back if an error occurs
                # Need to re-render with the form and formset to show errors
                return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

        else:
            messages.error(request, 'Error al actualizar el residente. Por favor, verifica los campos en el formulario o en las cantidades de medicamentos.')
            # Re-render with the form and formset to show errors
            return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

    else:
        form = ResidentForm(instance=resident)
        formset = ResidentMedicationFormSet(instance=resident)

    return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

# Use the resident_doses_view from the medication_dose app
# Note: This view now handles authorization internally
resident_doses_view = medication_dose_resident_doses_view