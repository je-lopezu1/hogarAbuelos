from django.db import models
from medications.models import Medication # Import Medication
from supplies.models import Supply # Import Supply

class Resident(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    medical_condition = models.CharField(max_length=300)
    # Changed to a ManyToManyField with a 'through' model
    medications = models.ManyToManyField(
        Medication,
        through='ResidentMedication',
        related_name='residents_with_quantity' # Changed related_name
    )
    supplies = models.ManyToManyField(
        Supply,
        through='ResidentSupply',
        related_name='residents_with_quantity' # Changed related_name
    )

    def __str__(self):
        return self.name

# New intermediary model to store quantity per resident per medication
class ResidentMedication(models.Model):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(default=0) # Quantity the resident has

    class Meta:
        unique_together = ('resident', 'medication') # A resident can only have one entry per medication

    def __str__(self):
        return f"{self.resident.name} - {self.medication.name} ({self.quantity_on_hand})"
    
# New intermediary model to sotre de quantity per resident per supply
class ResidentSupply(models.Model):
    resident = models.ForeignKey(Resident, on_delete=models.CASCADE)
    supply = models.ForeignKey(Supply, on_delete=models.CASCADE)
    quantity_on_hand = models.IntegerField(default=0) # Quantity the resident has

    class Meta:
        unique_together = ('resident', 'supply') # A resident can only have one entry per supply

    def __str__(self):
        return f"{self.resident.name} - {self.supply.name} ({self.quantity_on_hand})"