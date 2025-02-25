from ..models import Resident

def get_all_residents():
    return Resident.objects.all()

def create_resident(resident_data):
    resident = Resident.objects.create(name=resident_data['name'],
                            age=resident_data['age'],
                            medical_condition=resident_data['medical_condition'])
    
    resident.medications.set(resident_data['medications'])
    return resident

def delete_resident(resident_id):
    Resident.objects.get(id=resident_id).delete()

def update_resident(resident_id, resident_data):
    resident = Resident.objects.get(id=resident_id)
    resident.name = resident_data['name']
    resident.age = resident_data['age']
    resident.medical_condition = resident_data['medical_condition']
    resident.medications.set(resident_data['medications'])
    resident.save()
    
