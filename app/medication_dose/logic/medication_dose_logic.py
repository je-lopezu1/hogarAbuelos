from ..models import MedicationDose
from medications.models import Medication
# ResidentMedication is not directly used here for quantity logic


def get_all_resident_medication_doses(resident):
    # Ordering doses here
    return MedicationDose.objects.filter(resident=resident).order_by('-day', '-time')

def create_medication_dose(medication_dose_data):
    # Quantity check and deduction are done in the view BEFORE calling this function
    medication_dose = MedicationDose.objects.create(
        resident=medication_dose_data.get("resident"),
        medication=medication_dose_data.get("medication"),
        dose=medication_dose_data.get("dose"),
        quantity_administered=medication_dose_data.get("quantity_administered"),
        day=medication_dose_data.get("day"),
        time=medication_dose_data.get("time")
    )
    # The MedicationDose model's save method will set medication_name
    return medication_dose

def delete_medication_dose(medication_dose_id):
     # Quantity restoration is handled in the view BEFORE calling this function
     MedicationDose.objects.filter(id=medication_dose_id).delete()


def get_medication_dose(medication_dose_id):
    return MedicationDose.objects.get(id=medication_dose_id)

def update_medication_dose(medication_dose_id, medication_dose_data):
    # Quantity adjustments are handled by the MedicationDoseUpdateForm's save method
    # This function might be less necessary now if the form is the primary update mechanism.
    # Keeping it for now if there's other logic that might use it.
    medication_dose = get_medication_dose(medication_dose_id)
    # Update fields
    medication_dose.medication = medication_dose_data.get("medication")
    medication_dose.dose = medication_dose_data.get("dose")
    medication_dose.quantity_administered = medication_dose_data.get("quantity_administered")

    medication_dose.save() # The model's save method will handle medication_name

    return medication_dose