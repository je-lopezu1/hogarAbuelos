from django.db import models

# Importar modelos de residents y medications
from residents.models import Resident
from medications.models import Medication, MedicationInventory # Import MedicationInventory

# Crear modelo MedicationTrace
class MedicationDose(models.Model):
    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,  # Si se borra el residente, se borran sus dosis
        related_name='medication_doses',
        default=7 # Consider removing this default if you link doses to residents during creation
    )

    medication = models.ForeignKey(
        Medication,
        on_delete=models.SET_NULL,  # No elimina la dosis si se borra el medicamento
        null=True,
        blank=True
    )
    medication_name = models.CharField(max_length=255, editable=False)  # Guarda el nombre del medicamento, pero no se edita manualmente

    dose = models.CharField(max_length=50)
    quantity_administered = models.DecimalField(max_digits=10, decimal_places=2, default=1) # New field for quantity
    day = models.DateField()
    time = models.TimeField()

    def save(self, *args, **kwargs):
        # If there is a medication associated, save its name
        if self.medication:
            self.medication_name = self.medication.name

            # Only update inventory if it's a new dose or the medication/quantity changed
            if self._state.adding:
                # Decrease inventory when a new dose is saved
                try:
                    inventory = self.medication.inventory
                    inventory.quantity -= self.quantity_administered
                    inventory.save()
                except MedicationInventory.DoesNotExist:
                    print(f"Warning: Inventory not found for medication {self.medication.name}. Inventory not updated.")


        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.medication_name} - {self.dose} ({self.quantity_administered}) - {self.day} - {self.time}'