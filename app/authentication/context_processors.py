from authentication.models import UserProfile

def user_profile_context(request):
    """
    Agrega el perfil de usuario al contexto para acceder desde cualquier template.
    """
    if request.user.is_authenticated:
        try:
            profile = request.user.profile
            return {
                'user_profile': profile,
                'is_doctor': profile.is_doctor(),
                'is_patient': profile.is_patient(),
                'is_family': profile.is_family(),
            }
        except UserProfile.DoesNotExist:
            # Si el usuario no tiene perfil, devolver valores por defecto
            return {
                'user_profile': None,
                'is_doctor': False,
                'is_patient': False,
                'is_family': False,
            }
    
    # Usuario no autenticado
    return {
        'user_profile': None,
        'is_doctor': False,
        'is_patient': False,
        'is_family': False,
    }