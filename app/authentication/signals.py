from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Crear un perfil de usuario automáticamente cuando se crea un usuario nuevo
    desde el admin u otro lugar que no sea el formulario de registro.
    """
    if created:
        # Verificar si ya existe un perfil para este usuario (por si acaso)
        if not UserProfile.objects.filter(user=instance).exists():
            # Set a default user type, perhaps 'family' or 'administrator' depending on your default
            # Let's set it to 'family' as a safe default if no other type is specified.
            UserProfile.objects.create(user=instance, user_type='family')