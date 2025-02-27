from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('dashboard/admin/', views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('dashboard/staff/', views.StaffDashboardView.as_view(), name='staff_dashboard'),
    path('dashboard/family/', views.FamilyDashboardView.as_view(), name='family_dashboard'),
]