from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required # Import login_required
from django.db import transaction # Import transaction for atomic updates

from medication_dose.models import MedicationDose
from medication_dose.forms import MedicationDoseForm, MedicationDoseUpdateForm
from residents.models import Resident
import medication_dose.logic.medication_dose_logic as mdl
from datetime import datetime
from authentication.models import UserProfile # Import UserProfile
from medications.models import MedicationInventory # Import for inventory check

@login_required
def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)

    # Basic authorization check: Ensure the user is allowed to view this resident's doses
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
            quantity_administered = form.cleaned_data.get('quantity_administered') # Get quantity

            # Check if enough medication is in stock
            try:
                inventory = medication.inventory
                if inventory.quantity < quantity_administered:
                    messages.error(request, f'No hay suficiente "{medication.name}" en inventario. Disponible: {inventory.quantity}')
                    return render(request, 'create_dose.html', {'resident': resident, 'form': form})
            except MedicationInventory.DoesNotExist:
                 messages.error(request, f'Inventario no encontrado para "{medication.name}". No se puede agregar la dosis.')
                 return render(request, 'create_dose.html', {'resident': resident, 'form': form})


            day = datetime.today().date()
            time = datetime.today().time()

            medication_dose_data = {
                'resident': resident,
                'medication': medication,
                'dose': dose,
                'quantity_administered': quantity_administered, # Include quantity
                'day': day,
                'time': time,
            }

            # Use a transaction to ensure inventory and dose are updated together
            try:
                with transaction.atomic():
                    mdl.create_medication_dose(medication_dose_data)
                    messages.success(request, 'Dosis agregada correctamente y inventario actualizado.')
                    return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)
            except Exception as e:
                messages.error(request, f'Error al guardar la dosis o actualizar el inventario: {e}')
                # The transaction will roll back any changes if an error occurs

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
        try:
            # Use a transaction for deletion and inventory update
            with transaction.atomic():
                # Before deleting, restore the quantity to the inventory
                if dose.medication:
                     try:
                        inventory = dose.medication.inventory
                        inventory.quantity += dose.quantity_administered
                        inventory.save()
                        messages.success(request, 'Dosis eliminada y inventario restaurado correctamente.')
                     except MedicationInventory.DoesNotExist:
                        messages.warning(request, f'Inventario no encontrado para "{dose.medication.name}". Dosis eliminada, pero inventario no actualizado.')
                else:
                     messages.warning(request, 'Dosis eliminada, pero no se pudo actualizar el inventario (medicamento no encontrado).')

                mdl.delete_medication_dose(dose_pk)


            return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)

        except Exception as e:
             messages.error(request, f'Error al eliminar la dosis: {e}')
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
        form = MedicationDoseUpdateForm(request.POST, instance=dose, resident=resident) # Pass resident and instance
        if form.is_valid():
            new_medication = form.cleaned_data.get('medication')
            new_quantity = form.cleaned_data.get('quantity_administered')

            # Get original quantity before saving the form
            original_quantity = dose.quantity_administered
            original_medication = dose.medication

            # Check if enough medication is in stock for the new quantity
            # This check is slightly more complex because we need to account for the original quantity
            if new_medication: # Ensure the medication is not set to None
                 try:
                    inventory = new_medication.inventory
                    # Calculate required stock adjustment: (new quantity - original quantity)
                    quantity_needed = new_quantity - original_quantity

                    if inventory.quantity < quantity_needed:
                        messages.error(request, f'No hay suficiente "{new_medication.name}" en inventario para esta actualización. Disponible: {inventory.quantity}')
                        return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})

                 except MedicationInventory.DoesNotExist:
                    messages.error(request, f'Inventario no encontrado para "{new_medication.name}". No se puede actualizar la dosis.')
                    return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})


            # Use a transaction for atomic update
            try:
                 with transaction.atomic():
                     # The form's save method with the custom save logic for DoseUpdateForm handles the inventory adjustment
                     form.save()
                     messages.success(request, 'Dosis actualizada correctamente.')
                     return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

            except Exception as e:
                messages.error(request, f'Error al actualizar la dosis: {e}')


        else:
            messages.error(request, 'Error al actualizar la dosis. Por favor, verifica los campos.')
    else:
        form = MedicationDoseUpdateForm(instance=dose, resident=resident) # Pass instance and resident

    context = {
        'form': form,
        'dose': dose,
        'resident': resident,
    }
    return render(request, 'update_dose.html', context)