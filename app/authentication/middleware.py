from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.urls.exceptions import Resolver404
from authentication.models import UserProfile # Make sure UserProfile is imported

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
        'residents:create_resident_view': ['administrator'], # <--- This is already restricted to 'administrator'
        'residents:update_resident_view': ['administrator'], # Only Admin updates
        'residents:delete_resident_view': ['administrator'], # Only Admin deletes
        'medications:medications_view': ['doctor', 'administrator'],
        'medications:create_medication_view': ['administrator'], # Only Admin creates medications
        'medications:update_medication_view': ['administrator'], # Only Admin updates medications
        'medications:delete_medication_view': ['administrator'], # Only Admin deletes medications
        'authentication:signup': ['administrator'], # Only Admin creates users
        'authentication:create': ['administrator'], # Assuming create is same as signup and restricted

        # Medication Dose views accessible to Doctor and Administrator (view only for Admin)
        # Family can also view resident doses
        'medication_dose:resident_doses_view': ['doctor', 'administrator', 'family'],
        'medication_dose:create_medication_dose_view': ['doctor'], # Only Doctor creates doses (This view is removed now, but the restriction is here)
        'medication_dose:update_medication_dose_view': ['doctor'], # Only Doctor updates doses
        'medication_dose:delete_medication_dose_view': ['doctor'], # Only Doctor deletes doses

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
                    return redirect('dashboard:index') # Redirect to dashboard if not allowed
            except UserProfile.DoesNotExist:
                # messages.error(request, 'Perfil de usuario no encontrado.') # Optional: Add a message
                return redirect('dashboard:index') # Redirect to dashboard if no profile exists

        return None