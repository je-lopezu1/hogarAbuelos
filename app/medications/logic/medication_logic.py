from ..models import Medication

def get_all_medications():
    return Medication.objects.all()

def create_medication(medication_data):
    Medication.objects.create(name=medication_data['name'])

def delete_medication(medication_id):
    Medication.objects.get(id=medication_id).delete()

def update_medication(medication_id, medication_data):
    medication = Medication.objects.get(id=medication_id)
    medication.name = medication_data['name']
    medication.save()
