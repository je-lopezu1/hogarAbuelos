from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction
from django.contrib import messages

from .models import Supply
from residents.models import Resident, ResidentSupply
from .forms import SupplyForm
from residents.forms import AddResidentSupplyQuantityForm
from supplies.logic import supplies_logic as sl
from django.core import serializers
from django.http import HttpResponse

def supplies_view(request):
    if request.method == 'GET':
        supplies = sl.get_all_supplies()
        return render(request, 'list_supplies.html', {'supplies': supplies})
    return render(request, 'list_supplies.html', {'supplies': supplies})

def create_supply_view(request):
    if request.method == 'POST':
        form = SupplyForm(request.POST)
        if form.is_valid():
            nombre = form.cleaned_data['name']
            sl.create_supply({'name': nombre})
            return redirect('supplies:supplies_view')
    else:
        form = SupplyForm()

    return render(request, 'create_supply.html', {'form': form})

def delete_supply_view(request, pk):
    if request.method == 'POST':
        supply = get_object_or_404(Supply, pk=pk)
        supply.delete()
        return redirect('supplies:supplies_view')
    return HttpResponse(status=405)

def update_supply_view(request, pk):
    supply = get_object_or_404(Supply, pk=pk)
    if request.method == 'POST':
        form = SupplyForm(request.POST, instance=supply)
        if form.is_valid():
            form.save()
            return redirect('supplies:supplies_view')
    else:
        form = SupplyForm(instance=supply)

    return render(request, 'update_supply.html', {'form': form})

def add_resident_supply_quantity_view(request, resident_pk):
    resident = get_object_or_404(Resident, pk=resident_pk)

    if not request.user.is_authenticated or not (hasattr(request.user, 'profile') and request.user.profile.is_administrator()):
        messages.error(request, "No tienes permiso para acceder a esta página.")
        return redirect('residents:resident_supplies_view')
    
    if request.method == 'POST':
        form = AddResidentSupplyQuantityForm(resident=resident)
        if form.is_valid():
            supply = form.cleaned_data['supply']
            quantity_to_add = form.cleaned_data['quantity_to_add']

            try:
                with transaction.atomic():
                    resident_supply = ResidentSupply.objects.select_for_update().get(
                        resident=resident,
                        supply=supply
                    )

                    resident_supply.quantity_on_hand += quantity_to_add
                    resident_supply.save()

                    messages.success(request, f"Se ha añadido {quantity_to_add} unidades de {supply.name} al residente {resident.name}.")
                    return redirect('residents:resident_supplies_view', resident_pk=resident.pk)
            
            except ResidentSupply.DoesNotExist:
                messages.error(request, f"El residente {resident.name} no tiene asignado el insumo {supply.name}.")
            except Exception as e:
                messages.error(request, f"Error al añadir cantidad: {e}")
        else:
            messages.error(request, "Formulario inválido. Por favor, revisa los datos.")

    return redirect('residents:resident_supplies_view', resident_pk=resident.pk)