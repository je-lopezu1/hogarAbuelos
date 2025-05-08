from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required # Import login_required
from authentication.models import UserProfile
from residents.models import Resident
from medication_dose.models import MedicationDose
from medications.models import Medication, MedicationInventory # Import MedicationInventory
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages # Import messages
from django.db.models import Count # Import Count

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        messages.error(request, 'Perfil de usuario no encontrado. Contacte al administrador.')
        return render(request, 'dashboard/error.html', {'error': 'Perfil de usuario no encontrado'})

    if profile.is_doctor():
        return doctor_dashboard(request, profile)
    elif profile.is_administrator():
        return administrator_dashboard(request, profile)
    elif profile.is_family():
        return family_dashboard(request, profile)
    else:
        messages.error(request, 'Tipo de usuario no válido. Contacte al administrador.')
        return render(request, 'dashboard/error.html', {'error': 'Tipo de usuario no válido'})

def doctor_dashboard(request, profile):
    residents = Resident.objects.all()
    total_residents = residents.count()

    # Get most prescribed medications (across all residents)
    # We need Medication objects to access inventory
    top_medications_data = Medication.objects.annotate(resident_count=Count('residents')).order_by('-resident_count')[:5]

    # Prepare a dictionary to easily access medication objects by name in the template
    medications_by_name = {med.name: med for med in Medication.objects.all()}


    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'total_residents': total_residents,
        'top_medications_data': top_medications_data, # Pass the annotated queryset
        'medications_by_name': medications_by_name, # Pass dictionary for quick lookup
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)

def administrator_dashboard(request, profile):
    residents = Resident.objects.all()
    total_residents = residents.count()

    # Get most assigned medications (across all residents)
    # We need Medication objects to access inventory
    top_medications_data = Medication.objects.annotate(resident_count=Count('residents')).order_by('-resident_count')[:5]

    # Prepare a dictionary to easily access medication objects by name in the template
    medications_by_name = {med.name: med for med in Medication.objects.all()}


    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'total_residents': total_residents,
        'top_medications_data': top_medications_data, # Pass the annotated queryset
        'medications_by_name': medications_by_name, # Pass dictionary for quick lookup
        'recent_doses': recent_doses,
    }
    return render(request, 'dashboard/administrator_dashboard.html', context)

def family_dashboard(request, profile):
    residents = profile.related_residents.all()

    if not residents:
        messages.info(request, 'No hay residentes asociados a este usuario familiar.')
        return render(request, 'dashboard/family_dashboard.html', {'profile': profile, 'residents': residents, 'selected_resident': None})

    selected_resident_id = request.GET.get('resident_id')

    if selected_resident_id:
        try:
            selected_resident = residents.get(id=selected_resident_id)
        except Resident.DoesNotExist:
            selected_resident = residents.first()
            messages.warning(request, 'El residente seleccionado no está asociado a tu perfil. Mostrando información del primer residente asociado.')
    else:
        selected_resident = residents.first()

    if not selected_resident:
         messages.info(request, 'No hay residentes asociados a este usuario familiar.')
         return render(request, 'dashboard/family_dashboard.html', {'profile': profile, 'residents': residents, 'selected_resident': None})

    medications = selected_resident.medications.all()
    recent_doses = MedicationDose.objects.filter(resident=selected_resident).order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'selected_resident': selected_resident,
        'medications': medications.prefetch_related('inventory'), # Prefetch inventory for efficiency
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/family_dashboard.html', context)