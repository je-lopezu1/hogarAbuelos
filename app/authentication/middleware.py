from django.shortcuts import redirect
from django.urls import reverse, resolve
from django.utils.deprecation import MiddlewareMixin
from django.urls.exceptions import Resolver404

class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware para controlar el acceso a ciertas páginas según el rol del usuario.
    """
    
    # Páginas públicas (no requieren autenticación)
    PUBLIC_URLS = [
        'index',
        'authentication:login',
        'authentication:signup',
        'authentication:logout',
    ]
    
    # Páginas restringidas por rol
    RESTRICTED_URLS = {
        'residents:residents_view': ['doctor'],
        'residents:create_resident_view': ['doctor'],
        'residents:update_resident_view': ['doctor'],
        'residents:delete_resident_view': ['doctor'],
        'medications:medications_view': ['doctor'],
        'medications:create_medication_view': ['doctor'],
        'medications:update_medication_view': ['doctor'],
        'medications:delete_medication_view': ['doctor'],
    }
    
    def process_request(self, request):
        # Si es una URL estática o administrativa, continuar normalmente
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Intentar resolver la URL actual
        try:
            url_name = resolve(request.path).url_name
            namespace = resolve(request.path).namespace
            full_url_name = f"{namespace}:{url_name}" if namespace else url_name
        except Resolver404:
            return None
        
        # Si es una URL pública, continuar normalmente
        if url_name in self.PUBLIC_URLS or full_url_name in self.PUBLIC_URLS:
            return None
            
        # Si el usuario no está autenticado, redirigir al login
        if not request.user.is_authenticated:
            return redirect(f"{reverse('authentication:login')}?next={request.path}")
            
        # Si es un superusuario, permitir acceso a todo
        if request.user.is_superuser:
            return None
            
        # Verificar restricciones específicas por rol
        if full_url_name in self.RESTRICTED_URLS:
            allowed_roles = self.RESTRICTED_URLS[full_url_name]
            
            try:
                user_type = request.user.profile.user_type
                if user_type not in allowed_roles:
                    return redirect('dashboard:index')
            except:
                return redirect('dashboard:index')
                
        return None