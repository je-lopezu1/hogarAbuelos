from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime

from medication_dose.models import MedicationDose
from medication_dose.forms import MedicationDoseForm, MedicationDoseUpdateForm # Keep MedicationDoseForm for use in resident_doses_view
from residents.models import Resident, ResidentMedication
import medication_dose.logic.medication_dose_logic as mdl
from authentication.models import UserProfile
from medications.models import Medication


@login_required
def resident_doses_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)

    try:
        user_profile = request.user.profile
        # Authorization check: Admin and Doctor can view all. Family can view related.
        if not user_profile.is_doctor() and not user_profile.is_administrator():
             if user_profile.is_family() and resident not in user_profile.related_residents.all():
                 messages.error(request, 'No tienes permiso para ver las dosis de este residente.')
                 return redirect('dashboard:index')
             elif not user_profile.is_family():
                  messages.error(request, 'Tipo de usuario no autorizado para ver esta página.')
                  return redirect('dashboard:index')

    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado.')
        return redirect('dashboard:index')

    # Handle the form submission for adding a new dose
    if request.method == 'POST' and user_profile.is_doctor(): # Only doctors can add doses
        form = MedicationDoseForm(request.POST, resident=resident)
        if form.is_valid():
            medication = form.cleaned_data.get('medication')
            quantity_administered = form.cleaned_data.get('quantity_administered')

            # Check if the resident has enough of this medication
            try:
                resident_medication = ResidentMedication.objects.select_for_update().get( # Use select_for_update in transaction
                    resident=resident,
                    medication=medication
                )
                if resident_medication.quantity_on_hand < quantity_administered:
                    messages.error(request, f'"{resident.name}" no tiene suficiente "{medication.name}" ({resident_medication.quantity_on_hand}). No se pudo agregar la dosis.')
                    # Proceed to render the page with the form and errors
                else:
                    day = datetime.today().date()
                    time = datetime.today().time()

                    medication_dose_data = {
                        'resident': resident,
                        'medication': medication,
                        'dose': form.cleaned_data.get('dose'),
                        'quantity_administered': quantity_administered,
                        'day': day,
                        'time': time,
                    }

                    try:
                        with transaction.atomic():
                            # Deduct quantity BEFORE creating the dose within the transaction
                            resident_medication.quantity_on_hand -= quantity_administered
                            resident_medication.save()

                            # Create the dose
                            mdl.create_medication_dose(medication_dose_data)

                            messages.success(request, 'Dosis agregada correctamente.')
                            # Redirect to the same page to clear the form and show updated data
                            return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

                    except Exception as e:
                        messages.error(request, f'Error al guardar la dosis: {e}')
                        # The atomic block will roll back if an error occurs
                        # Proceed to render the page with the form and errors


            except ResidentMedication.DoesNotExist:
                 messages.error(request, f'"{resident.name}" no tiene "{medication.name}" asignado o no se encontró el registro de cantidad.')
                 # Proceed to render the page with the form and errors

        else:
             messages.error(request, 'Error al agregar la dosis. Por favor, verifica los campos.')
             # Proceed to render the page with the form and errors

    else: # GET request or non-doctor POST
        form = MedicationDoseForm(resident=resident) # Initialize an empty form

    # Fetch doses and resident medications for rendering the page
    doses = MedicationDose.objects.filter(resident=resident).order_by('-day', '-time')
    resident_medications = ResidentMedication.objects.filter(resident=resident).select_related('medication')

    context = {
        'resident': resident,
        'doses': doses,
        'resident_medications': resident_medications,
        'form': form, # Pass the form to the template
    }

    return render(request, 'resident_doses.html', context)

# The create_medication_dose_view is removed as its logic is now in resident_doses_view

@login_required
def delete_medication_dose_view(request, resident_pk, dose_pk):
    # Access restricted to 'doctor' by middleware
    dose = get_object_or_404(MedicationDose, pk=dose_pk)

    if dose.resident.pk != resident_pk:
         messages.error(request, 'La dosis no corresponde al residente indicado.')
         return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)

    if request.method == 'POST':
        try:
             with transaction.atomic():
                 # Restore resident's medication quantity BEFORE deleting the dose within the transaction
                 if dose.medication and dose.quantity_administered is not None:
                     try:
                         resident_medication = ResidentMedication.objects.select_for_update().get( # Use select_for_update
                             resident=dose.resident,
                             medication=dose.medication
                         )
                         resident_medication.quantity_on_hand += dose.quantity_administered
                         resident_medication.save()
                         messages.success(request, 'Dosis eliminada y cantidad restaurada correctamente.')
                     except ResidentMedication.DoesNotExist:
                         messages.warning(request, f'ResidentMedication not found for {dose.resident.name} and {dose.medication_name}. Dose deleted, but quantity not restored.')
                 else:
                     messages.warning(request, 'Dosis eliminada, but could not restore quantity (medication or quantity missing).')

                 # Delete the dose
                 dose.delete()


             return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)

        except Exception as e:
             messages.error(request, f'Error al eliminar la dosis: {e}')
             return redirect('medication_dose:resident_doses_view', resident_pk=resident_pk)

    return HttpResponse(status=405)

@login_required
def update_medication_dose_view(request, resident_pk, dose_pk):
    # Access restricted to 'doctor' by middleware
    dose = get_object_or_404(MedicationDose, pk=dose_pk)
    resident = get_object_or_404(Resident, pk=resident_pk)

    if dose.resident.pk != resident.pk:
        messages.error(request, 'La dosis no corresponde al residente seleccionado.')
        return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

    if request.method == 'POST':
        form = MedicationDoseUpdateForm(request.POST, instance=dose, resident=resident)
        if form.is_valid():
            new_medication = form.cleaned_data.get('medication')
            new_quantity = form.cleaned_data.get('quantity_administered')

            original_quantity = dose.quantity_administered
            original_medication = dose.medication

            # Check if enough quantity is available for the net change BEFORE saving
            try:
                 with transaction.atomic(): # Include quantity check within the transaction
                     # Get the ResidentMedication instance for the medication *after* the update
                     new_resident_medication = ResidentMedication.objects.select_for_update().get( # Use select_for_update
                         resident=resident,
                         medication=new_medication # Use the new medication for the check
                     )

                     # Calculate the net change required in the resident's quantity
                     # If medication changed, we first restore the original quantity, then deduct the new.
                     # If medication is the same, we deduct the difference.
                     if original_medication == new_medication:
                          # Check if there's enough for the additional quantity needed (if any)
                          quantity_needed = new_quantity - original_quantity
                          if resident_medication.quantity_on_hand < quantity_needed:
                              messages.error(request, f'"{resident.name}" no tiene suficiente "{new_medication.name}" ({resident_medication.quantity_on_hand}) para esta actualización ({quantity_needed} adicionales necesarios).')
                              # Render here with form to show the error
                              return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})
                     else:
                         # If medication changed, we need enough of the new medication for the full new quantity
                         if new_resident_medication.quantity_on_hand < new_quantity:
                              messages.error(request, f'"{resident.name}" no tiene suficiente "{new_medication.name}" ({new_resident_medication.quantity_on_hand}) para esta actualización ({new_quantity} necesarios).')
                              # Render here with form to show the error
                              return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})

                     # If validation passes, perform the quantity adjustments
                     # Restore original quantity if medication changed
                     if original_medication and original_medication != new_medication:
                         try:
                             original_resident_medication = ResidentMedication.objects.select_for_update().get(
                                 resident=resident,
                                 medication=original_medication
                             )
                             original_resident_medication.quantity_on_hand += original_quantity
                             original_resident_medication.save()
                         except ResidentMedication.DoesNotExist:
                              print(f"Warning: Original ResidentMedication not found for {resident.name} and {original_medication.name}. Quantity not restored on edit.")

                     # Deduct new quantity from the new medication's stock
                     # This is already handled by the check above if medication is the same
                     if original_medication == new_medication:
                          new_resident_medication.quantity_on_hand -= quantity_needed # Deduct the difference
                          new_resident_medication.save()
                     else: # If medication changed, we already checked for the full new quantity
                         new_resident_medication.quantity_on_hand -= new_quantity
                         new_resident_medication.save()


                     # Save the dose instance AFTER quantity adjustments
                     form.save() # The form's save method will now just save the dose fields

                     messages.success(request, 'Dosis actualizada correctamente.')
                     return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

            except ResidentMedication.DoesNotExist:
                 messages.error(request, f'El residente no tiene asignado el medicamento seleccionado ({new_medication.name}).')
                 return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})
            except Exception as e:
                messages.error(request, f'Error al actualizar la dosis: {e}')
                return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})


        else:
            messages.error(request, 'Error al actualizar la dosis. Por favor, verifica los campos.')
            return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})
    else:
        form = MedicationDoseUpdateForm(instance=dose, resident=resident)

    context = {
        'form': form,
        'dose': dose,
        'resident': resident,
    }
    return render(request, 'update_dose.html', context)