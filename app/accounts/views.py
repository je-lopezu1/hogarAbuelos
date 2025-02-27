from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.utils.translation import gettext_lazy as _

from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .models import CustomUser

class CustomLoginView(SuccessMessageMixin, LoginView):
    """Vista personalizada de inicio de sesión"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_message = _("Inicio de sesión exitoso.")
    
    def get_success_url(self):
        """Redirecciona según el tipo de usuario"""
        user = self.request.user
        if user.is_admin:
            return reverse_lazy('admin_dashboard')
        elif user.is_staff_member:
            return reverse_lazy('staff_dashboard')
        else:
            return reverse_lazy('family_dashboard')

class CustomLogoutView(LogoutView):
    """Vista de cierre de sesión"""
    next_page = reverse_lazy('login')

class RegisterView(SuccessMessageMixin, CreateView):
    """Vista de registro de usuarios"""
    form_class = CustomUserCreationForm
    template_name = 'accounts/register.html'
    success_url = reverse_lazy('login')
    success_message = _("Registro exitoso. Ahora puede iniciar sesión.")

class AdminDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard para administradores"""
    template_name = 'accounts/admin_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_admin:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class StaffDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard para personal"""
    template_name = 'accounts/staff_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff_member:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)

class FamilyDashboardView(LoginRequiredMixin, TemplateView):
    """Dashboard para familiares"""
    template_name = 'accounts/family_dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_family_member:
            return redirect('login')
        return super().dispatch(request, *args, **kwargs)