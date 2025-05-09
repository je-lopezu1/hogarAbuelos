from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.forms import inlineformset_factory
from django.db import transaction
from django import forms

from .forms import ResidentForm, ResidentMedicationForm
from residents.models import Resident, ResidentMedication, ResidentSupply
from residents.logic import residents_logic as rl
from authentication.models import UserProfile
from medication_dose.views import resident_doses_view as medication_dose_resident_doses_view
from medications.models import Medication
from supplies.models import Supply

@login_required
def residents_view(request):
    # This view is accessible to 'doctor', 'administrator' via middleware
    residents = rl.get_all_residents()
    residents = residents.prefetch_related('residentmedication_set__medication')
    residents = residents.prefetch_related('residentsupply_set__supply')
    return render(request, 'list_residents.html', {'residents': residents})

@login_required # This decorator is needed
def create_resident_view(request):
    # This view is accessible only to 'administrator' via RoleBasedAccessMiddleware
    # The logic here handles the form and data processing for creation.
    # The middleware ensures only admins reach this point.

    if request.method == 'POST':
        form = ResidentForm(request.POST)
        selected_medication_ids = request.POST.getlist('medications')
        selected_supply_ids = request.POST.getlist('supplies')
        initial_quantities = {}
        initial_quantities2 = {}
        quantity_errors = False
        quantity_errors2 = False
        for med_id in selected_medication_ids:
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
        
        for supply_id in selected_supply_ids:
                quantity_str2 = request.POST.get(f'initial_quantity_{supply_id}', '0')
                try:
                    quantity2 = int(quantity_str2)
                    if quantity2 < 0:
                        messages.error(request, f"La cantidad inicial para el insumo con ID {supply_id} no puede ser negativa.")
                        quantity_errors2 = True
                    initial_quantities2[int(supply_id)] = quantity2
                except ValueError:
                    messages.error(request, f"La cantidad inicial para el insumo con ID {supply_id} no es un número válido.")
                    quantity_errors2 = True

        if quantity_errors:
            form = ResidentForm(request.POST)
            all_medications = Medication.objects.all()
            all_supplies = Supply.objects.all()
            return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications, 'all_supplies': all_supplies})
        
        if quantity_errors2:
            form = ResidentForm(request.POST)
            all_medications = Medication.objects.all()
            all_supplies = Supply.objects.all()
            return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications, 'all_supplies': all_supplies})


        if form.is_valid() and not quantity_errors and not quantity_errors2:
            try:
                with transaction.atomic():
                    resident = form.save(commit=False)
                    resident.save()

                    for med_id, quantity in initial_quantities.items():
                         medication = get_object_or_404(Medication, pk=med_id)
                         ResidentMedication.objects.create(
                             resident=resident,
                             medication=medication,
                             quantity_on_hand=quantity
                         )
                    
                    for sup_id, quantity2 in initial_quantities2.items():
                         supply = get_object_or_404(Supply, pk=sup_id)
                         ResidentSupply.objects.create(
                             resident=resident,
                             supply=supply,
                             quantity_on_hand=quantity2
                         )

                    messages.success(request, f'Residente "{resident.name}" creado correctamente con medicamentos e insumos asignados.')
                    return redirect('residents:residents_view')

            except Exception as e:
                messages.error(request, f'Error al crear el residente o asignar medicamentos/insumos: {e}')
                all_medications = Medication.objects.all()
                all_supplies = Supply.objects.all()
                return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications, 'all_supplies': all_supplies})

        else:
            messages.error(request, 'Error al crear el residente. Por favor, verifica los campos.')
            all_medications = Medication.objects.all()
            all_supplies = Supply.objects.all()
            return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications, 'all_supplies': all_supplies})


    else:
        form = ResidentForm()

    all_medications = Medication.objects.all()
    all_supplies = Supply.objects.all()

    return render(request, 'create_resident.html', {'form': form, 'all_medications': all_medications, 'all_supplies': all_supplies})


@login_required
def delete_resident_view(request, pk):
    # This view is accessible only to 'administrator' via RoleBasedAccessMiddleware
    resident = get_object_or_404(Resident, pk=pk)
    if request.method == 'POST':
        try:
            resident_name = resident.name
            resident.delete()
            messages.success(request, f'Residente "{resident_name}" eliminado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al eliminar el residente: {e}')

        return redirect('residents:residents_view')
    return HttpResponse(status=405)

@login_required
def update_resident_view(request, pk):
    # This view is accessible only to 'administrator' via RoleBasedAccessMiddleware
    resident = get_object_or_404(Resident, pk=pk)
    ResidentMedicationFormSet = inlineformset_factory(
        Resident,
        ResidentMedication,
        form=ResidentMedicationForm,
        fields=['medication', 'quantity_on_hand'],
        extra=1,
        can_delete=True,
        widgets={
             'medication': forms.Select(attrs={'class': 'form-select form-select-sm'}),
        }
    )

    if request.method == 'POST':
        form = ResidentForm(request.POST, instance=resident)
        formset = ResidentMedicationFormSet(request.POST, instance=resident)

        if form.is_valid() and formset.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                    formset.save()
                    messages.success(request, f'Residente "{resident.name}" actualizado correctamente.')
                    return redirect('residents:residents_view')

            except Exception as e:
                messages.error(request, f'Error al actualizar el residente o sus medicamentos: {e}')
                return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

        else:
            messages.error(request, 'Error al actualizar el residente. Por favor, verifica los campos en el formulario o en las cantidades de medicamentos.')
            return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

    else:
        form = ResidentForm(instance=resident)
        formset = ResidentMedicationFormSet(instance=resident)

    return render(request, 'update_resident.html', {'form': form, 'formset': formset, 'resident': resident})

# Use the resident_doses_view from the medication_dose app
resident_doses_view = medication_dose_resident_doses_view

def resident_supplies_view(request, resident_pk):
    # This view is accessible to 'doctor', 'administrator' via middleware
    resident = get_object_or_404(Resident, pk=resident_pk)
    supplies = rl.get_all_resident_supplies(resident)
    return render(request, 'resident_supplies.html', {'resident': resident, 'supplies': supplies})