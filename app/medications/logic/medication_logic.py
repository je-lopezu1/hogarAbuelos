from ..models import Medication

def get_all_medications():
    return Medication.objects.all()

def create_medication(medication_data):
    Medication.objects.create(name=medication_data['name'])

def delete_medication(medication_id):
    Medication.objects.get(id=medication_id).delete()

