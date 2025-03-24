from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from authentication.models import UserProfile
from residents.models import Resident
from medication_dose.models import MedicationDose
from medications.models import Medication
from django.utils import timezone
from datetime import timedelta

@login_required
def dashboard_view(request):
    try:
        profile = request.user.profile
    except UserProfile.DoesNotExist:
        # Si no hay perfil, redirigir a página de error o creación de perfil
        return render(request, 'dashboard/error.html', {'error': 'Perfil de usuario no encontrado'})

    # Redireccionar según el tipo de usuario
    if profile.is_doctor():
        return doctor_dashboard(request, profile)
    elif profile.is_patient():
        return patient_dashboard(request, profile)
    elif profile.is_family():
        return family_dashboard(request, profile)
    else:
        return render(request, 'dashboard/error.html', {'error': 'Tipo de usuario no válido'})

def doctor_dashboard(request, profile):
    # Obtener todos los residentes
    residents = Resident.objects.all()

    # Calcular estadísticas básicas
    total_residents = residents.count()

    # Obtener medicamentos más recetados (across all residents)
    medications_count = {}
    for resident in residents:
        for med in resident.medications.all():
            if med.name in medications_count:
                medications_count[med.name] += 1
            else:
                medications_count[med.name] = 1

    top_medications = sorted(medications_count.items(), key=lambda x: x[1], reverse=True)[:5]

    # Obtener dosis recientes - ordenadas por día y hora
    recent_doses = MedicationDose.objects.all().order_by('-day', '-time')[:10]


    context = {
        'profile': profile,
        'residents': residents, # Pass all residents
        'total_residents': total_residents,
        'top_medications': top_medications,
        'recent_doses': recent_doses,
    }

    return render(request, 'dashboard/doctor_dashboard.html', context)

def patient_dashboard(request, profile):
    # Obtener el residente asociado al paciente
    resident = profile.resident

    if not resident:
        return render(request, 'dashboard/error.html', {'error': 'No hay perfil de residente asociado a este usuario'})

    # Obtener medicamentos del residente
    medications = resident.medications.all()

    # Obtener dosis recientes - ordenadas por día y hora
    recent_doses = MedicationDose.objects.filter(resident=resident).order_by('-day', '-time')[:10]

    # En lugar de usar un diccionario y el filtro get_item, creamos una lista de tuplas
    # con el medicamento y su última dosis
    medication_with_last_doses = []
    for medication in medications:
        last_dose = MedicationDose.objects.filter(
            resident=resident,
            medication=medication
        ).order_by('-day', '-time').first()

        medication_with_last_doses.append({
            'medication': medication,
            'last_dose': last_dose
        })

    context = {
        'profile': profile,
        'resident': resident,
        'medications': medications,
        'recent_doses': recent_doses,
        'medication_with_last_doses': medication_with_last_doses,
    }

    return render(request, 'dashboard/patient_dashboard.html', context)

def family_dashboard(request, profile):
    # Obtener residentes relacionados con el familiar
    residents = profile.related_residents.all()

    if not residents:
        return render(request, 'dashboard/error.html', {'error': 'No hay residentes asociados a este usuario familiar'})

    # Para simplificar, mostraremos información del primer residente relacionado
    selected_resident_id = request.GET.get('resident_id')

    if selected_resident_id:
        try:
            selected_resident = residents.get(id=selected_resident_id)
        except Resident.DoesNotExist:
            selected_resident = residents.first()
    else:
        selected_resident = residents.first()

    # Obtener medicamentos del residente
    medications = selected_resident.medications.all()

    # Obtener dosis recientes - ordenadas por día y hora
    recent_doses = MedicationDose.objects.filter(resident=selected_resident).order_by('-day', '-time')[:10]

    context = {
        'profile': profile,
        'residents': residents,
        'selected_resident': selected_resident,
        'medications': medications,
        'recent_doses': recent_doses,
        # Removed 'doctors': doctors from context
    }

    return render(request, 'dashboard/family_dashboard.html', context)