from django.db import models
from residents.models import Resident, ResidentMedication # Import ResidentMedication
from medications.models import Medication

class MedicationDose(models.Model):
    resident = models.ForeignKey(
        Resident,
        on_delete=models.CASCADE,
        related_name='medication_doses'
    )

    medication = models.ForeignKey(
        Medication,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    medication_name = models.CharField(max_length=255, editable=False)

    dose = models.CharField(max_length=50)
    quantity_administered = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    day = models.DateField()
    time = models.TimeField()

    def save(self, *args, **kwargs):
        # Set medication_name if medication is present
        if self.medication:
            self.medication_name = self.medication.name

            # Decrease resident's medication quantity when a NEW dose is saved
            # This logic is more robustly handled in the view with transactions and checks,
            # but keeping a basic version here as a safeguard if saving directly.
            if self._state.adding:
                try:
                    resident_medication = ResidentMedication.objects.get(
                        resident=self.resident,
                        medication=self.medication
                    )
                    if resident_medication.quantity_on_hand >= self.quantity_administered:
                        resident_medication.quantity_on_hand -= self.quantity_administered
                        resident_medication.save()
                    else:
                        # This case should ideally be prevented by view validation
                        print(f"Warning: Insufficient quantity for {self.resident.name}'s {self.medication.name}. Dose saved, but quantity might be negative.")
                except ResidentMedication.DoesNotExist:
                    print(f"Warning: ResidentMedication not found for {self.resident.name} and {self.medication.name}. Dose saved, but quantity not updated.")


        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
         # Restore resident's medication quantity when a dose is deleted
         if self.medication and self.quantity_administered is not None: # Ensure medication and quantity are available
             try:
                 resident_medication = ResidentMedication.objects.get(
                     resident=self.resident,
                     medication=self.medication
                 )
                 resident_medication.quantity_on_hand += self.quantity_administered
                 resident_medication.save()
                 print(f"Quantity restored for {self.resident.name}'s {self.medication.name} on dose deletion.")
             except ResidentMedication.DoesNotExist:
                 print(f"Warning: ResidentMedication not found for {self.resident.name} and {self.medication.name}. Dose deleted but quantity not restored.")

         super().delete(*args, **kwargs)


    def __str__(self):
        return f'{self.medication_name} - {self.dose} ({self.quantity_administered}) - {self.day} - {self.time}'