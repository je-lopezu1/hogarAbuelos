from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.urls.exceptions import Resolver404
from authentication.models import UserProfile

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware para controlar el acceso a ciertas páginas según el rol del usuario.
    """

    # Páginas públicas (no requieren autenticación)
    PUBLIC_URLS = [
        'index',
        'authentication:login',
        'authentication:logout',
    ]

    # Páginas restringidas por rol
    RESTRICTED_URLS = {
        # Administrator and Doctor can access these
        'residents:residents_view': ['doctor', 'administrator'],
        'residents:create_resident_view': ['administrator'],
        'residents:update_resident_view': ['administrator'],
        'residents:delete_resident_view': ['administrator'],
        'medications:medications_view': ['doctor', 'administrator'],
        'medications:create_medication_view': ['administrator'],
        'medications:update_medication_view': ['administrator'],
        'medications:delete_medication_view': ['administrator'],
        'authentication:signup': ['administrator'],
        'authentication:create': ['administrator'],

        # Medication Dose views accessible to Doctor and Administrator (view only for Admin)
        # Family can also view resident doses
        'medication_dose:resident_doses_view': ['doctor', 'administrator', 'family'],
        'medication_dose:update_medication_dose_view': ['doctor'],
        'medication_dose:delete_medication_dose_view': ['doctor'],
        'medication_dose:add_resident_medication_quantity_view': ['administrator'], # <--- Restrict adding quantity to Administrator

    }

    def process_request(self, request):
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None

        try:
            url_match = resolve(request.path)
            url_name = url_match.url_name
            namespace = url_match.namespace
            full_url_name = f"{namespace}:{url_name}" if namespace else url_name
        except Resolver404:
            return None

        if url_name in self.PUBLIC_URLS or full_url_name in self.PUBLIC_URLS:
            return None

        if not request.user.is_authenticated:
            return redirect(f"{reverse('authentication:login')}?next={request.path}")

        if request.user.is_superuser:
            return None

        if full_url_name in self.RESTRICTED_URLS:
            allowed_roles = self.RESTRICTED_URLS[full_url_name]

            try:
                user_profile = request.user.profile
                user_type = user_profile.user_type
                if user_type not in allowed_roles:
                    # messages.error(request, 'No tienes permiso para acceder a esta página.') # Optional: Add a message
                    return redirect('dashboard:index')
            except UserProfile.DoesNotExist:
                # messages.error(request, 'Perfil de usuario no encontrado.') # Optional: Add a message
                return redirect('dashboard:index')

        return None