from ..models import Medication

def get_all_medications():
    return Medication.objects.all()

def create_medication(medication_data):
    Medication.objects.create(name=medication_data['name'])

