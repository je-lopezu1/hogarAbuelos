from django.db import models

# Create your models here.
class Medication(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MedicationInventory(models.Model):
    medication = models.OneToOneField(
        Medication,
        on_delete=models.CASCADE,
        related_name='inventory'
    )
    quantity = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.medication.name} - {self.quantity} in stock'