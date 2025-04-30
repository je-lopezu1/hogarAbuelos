from django.db import models
from django.contrib.auth.models import User
from residents.models import Resident

class UserProfile(models.Model):
    USER_TYPE_CHOICES = (
        ('doctor', 'Doctor'),
        ('administrator', 'Administrador'), # Changed from 'patient'
        ('family', 'Familiar')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=13, choices=USER_TYPE_CHOICES) # Increased max_length
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)

    # If is administrator, they might be associated with residents for viewing purposes (optional)
    # If is patient, this field was used. Now it's for administrators viewing a specific resident
    resident = models.OneToOneField(
        Resident,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='administrator_profile' # Changed related_name
    )

    # If is family, se asocia con uno o más residentes
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

    def is_administrator(self): # New method
        return self.user_type == 'administrator'

    def is_family(self):
        return self.user_type == 'family'