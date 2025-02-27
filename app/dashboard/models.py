from django.db import models

# El dashboard no necesita modelos adicionales, pero podemos crear uno para
# guardar configuraciones o preferencias del usuario para su dashboard
class DashboardPreference(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name='dashboard_preference')
    show_medications_first = models.BooleanField(default=False)
    show_recent_doses = models.BooleanField(default=True)
    items_per_page = models.IntegerField(default=10)
    
    def __str__(self):
        return f"Dashboard preferences for {self.user.username}"