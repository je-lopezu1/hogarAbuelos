from django.db import models
from django.contrib.auth.models import User
from residents.models import Resident

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('patient', 'Paciente'),
        ('family', 'Familiar')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    # Si es paciente, se asocia directamente con un residente
    resident = models.OneToOneField(
        Resident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='patient_profile'
    )

    # Si es familiar, se asocia con uno o más residentes
    related_residents = models.ManyToManyField(
        Resident,
        blank=True,
        related_name='family_members'
    )

    specialty = models.CharField(max_length=100, blank=True)  # Solo para doctores
    relationship = models.CharField(max_length=50, blank=True)  # Solo para familiares

    def __str__(self):
        return f"{self.user.username} - {self.get_user_type_display()}"

    def is_doctor(self):
        return self.user_type == 'doctor'

    def is_patient(self):
        return self.user_type == 'patient'

    def is_family(self):
        return self.user_type == 'family'