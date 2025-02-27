from django import template
from authentication.models import UserProfile

register = template.Library()

@register.filter(name='has_role')
def has_role(user, role):
    """
    Verificar si un usuario tiene un rol específico.
    Uso en template: {% if user|has_role:'doctor' %}...{% endif %}
    """
    if not user.is_authenticated:
        return False
        
    try:
        if role == 'doctor':
            return user.profile.is_doctor()
        elif role == 'patient':
            return user.profile.is_patient()
        elif role == 'family':
            return user.profile.is_family()
        else:
            return False
    except UserProfile.DoesNotExist:
        return False

@register.filter(name='get_item')
def get_item(dictionary, key):
    """
    Obtener un elemento de un diccionario en un template.
    Uso: {{ my_dict|get_item:key_var }}
    """
    return dictionary.get(key)