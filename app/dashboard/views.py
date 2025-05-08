from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import UserProfile
from residents.models import Resident, ResidentMedication # Import ResidentMedication
from medication_dose.models import MedicationDose
from medications.models import Medication
from django.utils import timezone
from datetime import timedelta
from django.contrib import messages
from django.db.models import Count, Sum # Import Sum


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

    # Get most prescribed medications based on the number of residents assigned
    top_medications_data = Medication.objects.annotate(resident_count=Count('residents_with_quantity')).order_by('-resident_count')[:5]

    # Get recent doses - ordered by day and time for all residents
    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'total_residents': total_residents,
        'top_medications_data': top_medications_data,
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)

def administrator_dashboard(request, profile):
    residents = Resident.objects.all()
    total_residents = residents.count()

    # Get most assigned medications based on the number of residents assigned
    top_medications_data = Medication.objects.annotate(resident_count=Count('residents_with_quantity')).order_by('-resident_count')[:5]

    # Get recent doses - ordered by day and time for all residents
    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]

    # Get overall medication inventory summary (sum of quantities across all residents)
    # This requires aggregating across ResidentMedication
    overall_inventory_summary = ResidentMedication.objects.values('medication__name').annotate(total_quantity=Sum('quantity_on_hand')).order_by('-total_quantity')[:10]


    context = {
        'profile': profile,
        'residents': residents,
        'total_residents': total_residents,
        'top_medications_data': top_medications_data,
        'recent_doses': recent_doses,
        'overall_inventory_summary': overall_inventory_summary, # New context variable
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


    # Get medications assigned to the selected resident with their quantities
    resident_medications = ResidentMedication.objects.filter(resident=selected_resident).select_related('medication')
    assigned_medications = [rm.medication for rm in resident_medications] # Get the Medication objects

    # Get recent doses for the selected resident - ordered by day and time
    recent_doses = MedicationDose.objects.filter(resident=selected_resident).order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'selected_resident': selected_resident,
        'resident_medications': resident_medications, # Pass ResidentMedication objects with quantities
        'medications': assigned_medications, # Pass Medication objects for looping if needed
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/family_dashboard.html', context)