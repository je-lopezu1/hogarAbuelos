from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado con tipo de usuario
    """
    USER_TYPE_CHOICES = (
        ('admin', 'Administrador'),
        ('staff', 'Personal'),
        ('family', 'Familiar'),
    )
    
    user_type = models.CharField(
        _("Tipo de Usuario"),
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default='family',
    )
    
    phone = models.CharField(_("Teléfono"), max_length=20, blank=True, null=True)
    address = models.CharField(_("Dirección"), max_length=255, blank=True, null=True)
    
    # Si el usuario es familiar, puede estar relacionado con residentes
    related_resident = models.ForeignKey(
        'residents.Resident',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name=_("Residente Relacionado"),
        related_name="family_members"
    )
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_user_type_display()})"
    
    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        
    @property
    def is_admin(self):
        return self.user_type == 'admin'
    
    @property
    def is_staff_member(self):
        return self.user_type == 'staff'
    
    @property
    def is_family_member(self):
        return self.user_type == 'family'