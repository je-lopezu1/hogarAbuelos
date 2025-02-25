from django.db import models

# Create your models here.
class Resident(models.Model):
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    medical_condition = models.CharField(max_length=300)
    medications = models.ManyToManyField('medications.Medication', related_name='residents')

    def __str__(self):
        return self.name

