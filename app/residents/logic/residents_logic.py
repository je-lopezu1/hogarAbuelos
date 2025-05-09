from medication_dose.models import MedicationDose
from ..models import Resident

def get_all_residents():
    return Resident.objects.all()

def create_resident(resident_data):
    resident = Resident.objects.create(name=resident_data['name'],
                            age=resident_data['age'],
                            medical_condition=resident_data['medical_condition'])

    resident.medications.set(resident_data['medications'])
    resident.supplies.set(resident_data['supplies'])
    return resident

def delete_resident(resident_id):
    Resident.objects.get(id=resident_id).delete()

def update_resident(resident_id, resident_data):
    resident = Resident.objects.get(id=resident_id)
    resident.name = resident_data['name']
    resident.age = resident_data['age']
    resident.medical_condition = resident_data['medical_condition']
    resident.medications.set(resident_data['medications'])
    resident.supplies.set(resident_data['supplies'])
    resident.save()

def get_all_resident_medication_doses(resident):
    doses = MedicationDose.objects.filter(resident=resident).order_by('-day', '-time') # Ordering doses here
    return doses

def get_all_resident_supplies(resident):
    supplies_with_quantity = resident.supplies.through.objects.filter(resident=resident).select_related('supply')
    result = [
        {
            'name': supply.supply.name,  # Assuming the supply model has a 'name' field
            'quantity': supply.quantity_on_hand,
        }
        for supply in supplies_with_quantity
    ]
    return result