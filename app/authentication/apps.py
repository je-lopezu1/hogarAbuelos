from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    verbose_name = 'Autenticación y Perfiles'
    
    def ready(self):
        # Importar señales cuando la app esté lista
        import authentication.signals