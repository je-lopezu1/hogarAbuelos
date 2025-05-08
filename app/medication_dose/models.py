from django.db import models
from residents.models import Resident, ResidentMedication
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

    # New field to track dose status
    STATUS_CHOICES = [
        ('scheduled', 'Programada'),
        ('taken', 'Tomada'),
        ('skipped', 'Omitida'),
        ('deleted', 'Eliminada'), # Use 'deleted' to represent the logical deletion
    ]
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='scheduled')

    def save(self, *args, **kwargs):
        # Set medication_name if medication is present
        if self.medication:
            self.medication_name = self.medication.name

        # Quantity deduction logic is handled in the view on creation.
        # Quantity restoration logic is handled in the view on "deletion" (status change).

        super().save(*args, **kwargs)

    # Removed the delete method as we are not doing physical deletion
    # def delete(self, *args, **kwargs):
    #      # ... quantity restoration logic removed ...
    #      super().delete(*args, **kwargs)


    def __str__(self):
        return f'{self.medication_name} - {self.dose} ({self.quantity_administered}) - {self.day} - {self.time}'