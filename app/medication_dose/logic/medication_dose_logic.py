from ..models import MedicationDose
from medications.models import Medication
from medications.models import Medication
from medication_dose.models import MedicationDose

def get_all_resident_medication_doses(resident):
    return MedicationDose.objects.filter(resident=resident)

def create_medication_dose(medication_dose_data):
    resident = medication_dose_data.get("resident")
    medication = medication_dose_data.get("medication")
    dose = medication_dose_data.get("dose")
    day = medication_dose_data.get("day")
    time = medication_dose_data.get("time")


    if not medication or not dose:
        raise ValueError("Todos los campos son obligatorios: medicamento, dosis, día y hora")

    # Intentar obtener el objeto Medication
    medication = Medication.objects.filter(name = medication.name).first()

    medication_dose = MedicationDose.objects.create(
        resident=resident,
        medication=medication,  # Puede ser None si no existe en la BD
        medication_name=medication.name,  # Guarda el nombre aunque se elimine el medicamento
        dose=dose,
        day=day,
        time=time
    )

    return medication_dose


