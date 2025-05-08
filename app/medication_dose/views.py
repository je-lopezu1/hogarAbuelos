from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from datetime import datetime

from medication_dose.models import MedicationDose
from medication_dose.forms import MedicationDoseForm, MedicationDoseUpdateForm
from residents.models import Resident, ResidentMedication
from residents.forms import AddResidentMedicationQuantityForm
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

    # Initialize forms for display (GET request or POST with errors)
    medication_dose_form = None
    add_quantity_form = None

    # --- Handle POST requests ---
    if request.method == 'POST':
        if user_profile.is_doctor():
            # Handle Dose Form submission (only if doctor)
            medication_dose_form = MedicationDoseForm(request.POST, resident=resident)
            if medication_dose_form.is_valid():
                medication = medication_dose_form.cleaned_data.get('medication')
                quantity_administered = medication_dose_form.cleaned_data.get('quantity_administered')

                # Check if the resident has enough of this medication
                try:
                    resident_medication = ResidentMedication.objects.select_for_update().get(
                        resident=resident,
                        medication=medication
                    )
                    if resident_medication.quantity_on_hand < quantity_administered:
                        messages.error(request, f'"{resident.name}" no tiene suficiente "{medication.name}" ({resident_medication.quantity_on_hand}). No se pudo agregar la dosis.')
                        # The form and errors will be rendered below
                    else:
                        day = datetime.today().date()
                        time = datetime.today().time()

                        medication_dose_data = {
                            'resident': resident,
                            'medication': medication,
                            'dose': medication_dose_form.cleaned_data.get('dose'),
                            'quantity_administered': quantity_administered,
                            'day': day,
                            'time': time,
                            'status': 'scheduled', # Default status for new dose
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
                            # The form and errors will be rendered below


                except ResidentMedication.DoesNotExist:
                     messages.error(request, f'"{resident.name}" no tiene "{medication.name}" asignado o no se encontró el registro de cantidad.')
                     # The form and errors will be rendered below

            # If form is not valid or there's an error, it will fall through to render with the form
            add_quantity_form = AddResidentMedicationQuantityForm(resident=resident) # Initialize other form

        # Note: The add_resident_medication_quantity_view handles its own POST requests
        # and redirects. So, if an admin submits the quantity form, this block won't run.

    else: # --- Handle GET requests ---
        if user_profile.is_doctor():
            medication_dose_form = MedicationDoseForm(resident=resident)
        if user_profile.is_administrator():
            add_quantity_form = AddResidentMedicationQuantityForm(resident=resident)


    # Fetch doses - ONLY display doses that are NOT 'deleted'
    doses = MedicationDose.objects.filter(resident=resident).exclude(status='deleted').order_by('-day', '-time')

    # Fetch resident medications for rendering the quantity info
    resident_medications = ResidentMedication.objects.filter(resident=resident).select_related('medication')

    context = {
        'resident': resident,
        'doses': doses,
        'resident_medications': resident_medications,
        'medication_dose_form': medication_dose_form,
        'add_quantity_form': add_quantity_form,
    }

    return render(request, 'resident_doses.html', context)


@login_required
def add_resident_medication_quantity_view(request, resident_pk):
    # This view handles only the POST request for adding quantity
    # Restricted to Administrator by middleware
    resident = get_object_or_404(Resident, pk=resident_pk)

    # Ensure the user is an Administrator (redundant with middleware, but good practice)
    if not request.user.is_authenticated or not (hasattr(request.user, 'profile') and request.user.profile.is_administrator()):
         messages.error(request, 'No tienes permiso para realizar esta acción.')
         return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

    if request.method == 'POST':
        form = AddResidentMedicationQuantityForm(request.POST, resident=resident)
        if form.is_valid():
            medication = form.cleaned_data.get('medication')
            quantity_to_add = form.cleaned_data.get('quantity_to_add')

            try:
                with transaction.atomic():
                    resident_medication = ResidentMedication.objects.select_for_update().get(
                        resident=resident,
                        medication=medication
                    )
                    resident_medication.quantity_on_hand += quantity_to_add
                    resident_medication.save()

                    messages.success(request, f'Cantidad añadida a "{medication.name}" para {resident.name}.')
                    return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)

            except ResidentMedication.DoesNotExist:
                 messages.error(request, f'"{resident.name}" no tiene "{medication.name}" asignado o no se encontró el registro de cantidad.')
            except Exception as e:
                 messages.error(request, f'Error al añadir cantidad: {e}')

        else:
             messages.error(request, 'Error al añadir cantidad. Por favor, verifica los campos.')

    # Redirect back to the doses page in case of GET or errors
    return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)


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
                 # Restore resident's medication quantity
                 if dose.medication and dose.quantity_administered is not None:
                     try:
                         resident_medication = ResidentMedication.objects.select_for_update().get(
                             resident=dose.resident,
                             medication=dose.medication
                         )
                         resident_medication.quantity_on_hand += dose.quantity_administered
                         resident_medication.save()
                         messages.success(request, 'Cantidad restaurada al inventario del residente.')
                     except ResidentMedication.DoesNotExist:
                         messages.warning(request, f'ResidentMedication not found for {dose.resident.name} and {dose.medication_name}. Quantity not restored.')
                 else:
                     messages.warning(request, 'Could not restore quantity (medication or quantity missing).')

                 # Mark the dose as 'deleted' instead of physical deletion
                 dose.status = 'deleted'
                 dose.save()

                 messages.success(request, 'Dosis marcada como eliminada (historial conservado).')


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

    # Prevent updating doses that are not in 'scheduled' status
    if dose.status != 'scheduled':
        messages.warning(request, 'Solo se pueden editar dosis programadas.')
        return redirect('medication_dose:resident_doses_view', resident_pk=resident.pk)


    if request.method == 'POST':
        form = MedicationDoseUpdateForm(request.POST, instance=dose, resident=resident)
        if form.is_valid():
            new_medication = form.cleaned_data.get('medication')
            new_quantity = form.cleaned_data.get('quantity_administered')

            original_quantity = dose.quantity_administered
            original_medication = dose.medication

            try:
                 with transaction.atomic():
                     new_resident_medication = ResidentMedication.objects.select_for_update().get(
                         resident=resident,
                         medication=new_medication
                     )

                     if original_medication == new_medication:
                          quantity_needed = new_quantity - original_quantity
                          if resident_medication.quantity_on_hand < quantity_needed:
                              messages.error(request, f'"{resident.name}" no tiene suficiente "{new_medication.name}" ({new_resident_medication.quantity_on_hand}) para esta actualización ({quantity_needed} adicionales necesarios).')
                              return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})
                     else:
                         if new_resident_medication.quantity_on_hand < new_quantity:
                              messages.error(request, f'"{resident.name}" no tiene suficiente "{new_medication.name}" ({new_resident_medication.quantity_on_hand}) para esta actualización ({new_quantity} necesarios).')
                              return render(request, 'update_dose.html', {'form': form, 'dose': dose, 'resident': resident})

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

                     if original_medication == new_medication:
                          new_resident_medication.quantity_on_hand -= quantity_needed
                          new_resident_medication.save()
                     else:
                         new_resident_medication.quantity_on_hand -= new_quantity
                         new_resident_medication.save()

                     form.save() # Save the dose instance with updated fields
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