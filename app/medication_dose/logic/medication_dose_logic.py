from ..models import MedicationDose
from medications.models import Medication, MedicationInventory # Import MedicationInventory

def get_all_resident_medication_doses(resident):
    return MedicationDose.objects.filter(resident=resident).order_by('-day', '-time') # Ordering doses here

def create_medication_dose(medication_dose_data):
    resident = medication_dose_data.get("resident")
    medication = medication_dose_data.get("medication")
    dose_text = medication_dose_data.get("dose") # Renamed to avoid conflict
    quantity_administered = medication_dose_data.get("quantity_administered") # Get quantity
    day = medication_dose_data.get("day")
    time = medication_dose_data.get("time")

    if not medication or not dose_text or quantity_administered is None:
        # Added quantity_administered to check
        raise ValueError("Todos los campos son obligatorios: medicamento, dosis (texto), cantidad, día y hora")

    # Medication object is already passed from the form
    # No need to fetch it by name again here unless you need to ensure it exists
    # But the form's ModelChoiceField already ensures a valid Medication object is selected.

    # Check inventory before creating (already done in view, but good to have logic layer check too)
    try:
        inventory = medication.inventory
        if inventory.quantity < quantity_administered:
             raise ValueError(f'No hay suficiente "{medication.name}" en inventario. Disponible: {inventory.quantity}')
    except MedicationInventory.DoesNotExist:
        raise ValueError(f'Inventario no encontrado para "{medication.name}". No se puede agregar la dosis.')


    medication_dose = MedicationDose.objects.create(
        resident=resident,
        medication=medication,
        # medication_name is set automatically by the model's save method
        dose=dose_text,
        quantity_administered=quantity_administered, # Save quantity
        day=day,
        time=time
    )

    # Inventory update is handled in the MedicationDose model's save method
    # Consider removing the save method from the model and doing the inventory update explicitly here
    # within a transaction in the view for better control.
    # For now, keeping the model save method logic as requested by the original structure.

    return medication_dose

def delete_medication_dose(medication_dose_id):
     # Inventory restoration is handled in the view before calling this function
     MedicationDose.objects.filter(id=medication_dose_id).delete()

def get_medication_dose(medication_dose_id):
    return MedicationDose.objects.get(id=medication_dose_id)

def update_medication_dose(medication_dose_id, medication_dose_data):
    # Inventory adjustment is handled in the MedicationDoseUpdateForm's save method
    medication_dose = get_medication_dose(medication_dose_id)
    medication_dose.medication = medication_dose_data.get("medication")
    medication_dose.dose = medication_dose_data.get("dose")
    medication_dose.quantity_administered = medication_dose_data.get("quantity_administered") # Update quantity

    medication_dose.save() # The model's save method *might* re-adjust inventory if not careful,
                             # but the form's save method is intended to handle the net change.
                             # Relying on the form's save method for the primary inventory adjustment.

    return medication_dose