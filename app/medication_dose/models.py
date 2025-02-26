from django.db import models

# Importar modelos de residents y medications
from residents.models import Resident
from medications.models import Medication

# Crear modelo MedicationTrace
class MedicationDose(models.Model):
    resident = models.ForeignKey(
        Resident, 
        on_delete=models.CASCADE,  # Si se borra el residente, se borran sus dosis
        related_name='medication_doses',
        default=7
    )
    
    medication = models.ForeignKey(
        Medication, 
        on_delete=models.SET_NULL,  # No elimina la dosis si se borra el medicamento
        null=True, 
        blank=True
    )
    medication_name = models.CharField(max_length=255, editable=False)  # Guarda el nombre del medicamento, pero no se edita manualmente
    
    dose=models.CharField(max_length=50)
    day=models.DateField()
    time=models.TimeField()

    def save(self, *args, **kwargs):
        # Si hay un medicamento asociado, guarda su nombre
        if self.medication and not self.medication_name:  
            self.medication_name = self.medication.name  # Guarda el nombre solo si no está ya almacenado
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.medication_name} - {self.dose} - {self.day} - {self.time}'

