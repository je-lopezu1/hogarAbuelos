from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import UserProfile
from residents.models import Resident
from medication_dose.models import MedicationDose
from medications.models import Medication
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages # Import messages

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # If no profile, redirect to error page or profile creation
        # You might want to auto-create a basic profile for new users
        # The signal `create_user_profile` in authentication/signals.py attempts to do this
        messages.error(request, 'Perfil de usuario no encontrado. Contacte al administrador.')
        # Consider redirecting to a page where a profile can be created if that's part of your flow
        return render(request, 'dashboard/error.html', {'error': 'Perfil de usuario no encontrado'})

    # Redirect based on user type
    if profile.is_doctor():
        return doctor_dashboard(request, profile)
    elif profile.is_administrator(): # New dashboard view
        return administrator_dashboard(request, profile)
    elif profile.is_family():
        return family_dashboard(request, profile)
    else:
        messages.error(request, 'Tipo de usuario no válido. Contacte al administrador.')
        return render(request, 'dashboard/error.html', {'error': 'Tipo de usuario no válido'})

def doctor_dashboard(request, profile):
    # Get all residents (doctors have access to all)
    residents = Resident.objects.all()

    # Calculate basic stats
    total_residents = residents.count()

    # Get most prescribed medications (across all residents)
    medications_count = {}
    for resident in residents:
        for med in resident.medications.all():
            if med.name in medications_count:
                medications_count[med.name] += 1
            else:
                medications_count[med.name] = 1

    top_medications = sorted(medications_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # Get recent doses - ordered by day and time
    # Doctors see recent doses for all residents
    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents, # Pass all residents
        'total_residents': total_residents,
        'top_medications': top_medications,
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)

def administrator_dashboard(request, profile):
    # Administrator dashboard logic - similar to doctor, but with admin-specific actions
    # Get all residents
    residents = Resident.objects.all()

    # Calculate basic stats
    total_residents = residents.count()

    # Get most assigned medications (across all residents)
    medications_count = {}
    for resident in residents:
        for med in resident.medications.all():
            if med.name in medications_count:
                medications_count[med.name] += 1
            else:
                medications_count[med.name] = 1

    top_medications = sorted(medications_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # Get recent doses - ordered by day and time
    # Administrators see recent doses for all residents
    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents, # Pass all residents
        'total_residents': total_residents,
        'top_medications': top_medications,
        'recent_doses': recent_doses,
    }
    # Render a specific template for administrators
    return render(request, 'dashboard/administrator_dashboard.html', context)


def family_dashboard(request, profile):
    # Get residents related to the family member
    residents = profile.related_residents.all()

    if not residents:
        messages.info(request, 'No hay residentes asociados a este usuario familiar.')
        return render(request, 'dashboard/family_dashboard.html', {'profile': profile, 'residents': residents, 'selected_resident': None})

    # For simplicity, we'll show information of the first related resident or the one selected
    selected_resident_id = request.GET.get('resident_id')

    if selected_resident_id:
        try:
            selected_resident = residents.get(id=selected_resident_id)
        except Resident.DoesNotExist:
            # If the selected resident ID is not valid for this family member, default to the first one
            selected_resident = residents.first()
            messages.warning(request, 'El residente seleccionado no está asociado a tu perfil. Mostrando información del primer residente asociado.')
    else:
        selected_resident = residents.first() # Default to the first related resident

    if not selected_resident:
         messages.info(request, 'No hay residentes asociados a este usuario familiar.')
         return render(request, 'dashboard/family_dashboard.html', {'profile': profile, 'residents': residents, 'selected_resident': None})


    # Get medications for the selected resident
    medications = selected_resident.medications.all()

    # Get recent doses for the selected resident - ordered by day and time
    recent_doses = MedicationDose.objects.filter(resident=selected_resident).order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents, # Pass all related residents for selection
        'selected_resident': selected_resident,
        'medications': medications,
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/family_dashboard.html', context)