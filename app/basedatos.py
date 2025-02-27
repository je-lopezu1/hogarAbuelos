import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# Configurar entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')  # Cambia esto a tu configuración
django.setup()

# Importar modelos después de configurar Django
from django.contrib.auth.models import User
from residents.models import Resident
from medications.models import Medication
from medication_dose.models import MedicationDose
from authentication.models import UserProfile
from dashboard.models import DashboardPreference

# Función para crear medicamentos de muestra
def create_medications():
    medications = [
        'Paracetamol', 'Ibuprofeno', 'Aspirina', 'Omeprazol', 'Lorazepam',
        'Diazepam', 'Metformina', 'Enalapril', 'Losartan', 'Atorvastatina',
        'Simvastatina', 'Levotiroxina', 'Albuterol', 'Fluoxetina', 'Sertralina',
        'Esomeprazol', 'Amlodipino', 'Lisinopril', 'Metoprolol', 'Warfarina'
    ]
    
    print("Creando medicamentos...")
    created_medications = []
    
    for med_name in medications:
        medication, created = Medication.objects.get_or_create(name=med_name)
        created_medications.append(medication)
        if created:
            print(f"  Creado medicamento: {med_name}")
        else:
            print(f"  Medicamento ya existe: {med_name}")
    
    return created_medications

# Función para crear residentes de muestra
def create_residents():
    first_names = ['María', 'José', 'Antonio', 'Carmen', 'Juan', 'Ana', 'Francisco', 'Isabel', 
                  'Manuel', 'Dolores', 'Luis', 'Pilar', 'Miguel', 'Teresa', 'Carlos', 'Elena']
    
    last_names = ['García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez', 'Sánchez', 
                 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz', 'Hernández', 'Díaz', 'Moreno']
    
    medical_conditions = [
        'Hipertensión arterial', 'Diabetes mellitus tipo 2', 'Artritis', 'Parkinson',
        'Alzheimer leve', 'Insuficiencia cardíaca', 'EPOC', 'Osteoporosis',
        'Cataratas', 'Artrosis', 'Depresión', 'Ansiedad', 'Hipotiroidismo', 
        'Fibrilación auricular', 'Enfermedad renal crónica'
    ]
    
    print("Creando residentes...")
    created_residents = []
    
    for i in range(20):
        first_name = random.choice(first_names)
        last_name = random.choice(last_names)
        name = f"{first_name} {last_name}"
        age = random.randint(65, 95)
        condition = random.choice(medical_conditions)
        
        resident, created = Resident.objects.get_or_create(
            name=name,
            defaults={
                'age': age,
                'medical_condition': condition
            }
        )
        
        created_residents.append(resident)
        if created:
            print(f"  Creado residente: {name}, {age} años, {condition}")
        else:
            print(f"  Residente ya existe: {name}")
    
    return created_residents

# Función para asignar medicamentos aleatorios a los residentes
def assign_medications(residents, medications):
    print("Asignando medicamentos a residentes...")
    
    for resident in residents:
        # Limpiar medicamentos existentes para evitar duplicados
        resident.medications.clear()
        
        # Asignar entre 1 y 5 medicamentos aleatorios
        num_meds = random.randint(1, 5)
        selected_meds = random.sample(medications, num_meds)
        
        for med in selected_meds:
            resident.medications.add(med)
        
        print(f"  {resident.name} recibe {num_meds} medicamentos")
    
    return residents

# Función para crear usuarios y perfiles
def create_users_and_profiles(residents):
    print("Creando usuarios y perfiles...")
    
    # Crear médicos
    doctors = []
    for i in range(5):
        username = f"doctor{i+1}"
        email = f"doctor{i+1}@example.com"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f"Doctor{i+1}",
                'last_name': f"Apellido{i+1}"
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"  Creado usuario doctor: {username}")
        else:
            print(f"  Usuario doctor ya existe: {username}")
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'doctor',
                'specialty': random.choice(['Geriatría', 'Cardiología', 'Neurología', 'Medicina Interna', 'Psiquiatría'])
            }
        )
        
        if created:
            print(f"  Creado perfil para: {username}")
        
        # Asignar pacientes aleatorios (entre 3 y 8)
        profile.patients.clear()  # Limpiar pacientes existentes
        num_patients = random.randint(3, 8)
        assigned_patients = random.sample(residents, num_patients)
        
        for patient in assigned_patients:
            profile.patients.add(patient)
            
        print(f"  Doctor {username} asignado a {num_patients} pacientes")
        doctors.append(profile)
    
    # Crear pacientes (usuarios para residentes)
    for i, resident in enumerate(residents[:10]):  # Solo crear usuarios para los primeros 10 residentes
        username = f"paciente{i+1}"
        email = f"paciente{i+1}@example.com"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': resident.name.split()[0],
                'last_name': resident.name.split()[1] if len(resident.name.split()) > 1 else ""
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"  Creado usuario paciente: {username}")
        else:
            print(f"  Usuario paciente ya existe: {username}")
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'patient',
                'resident': resident
            }
        )
        
        if created:
            print(f"  Creado perfil para: {username}, asociado a residente: {resident.name}")
    
    # Crear familiares
    for i in range(8):
        username = f"familiar{i+1}"
        email = f"familiar{i+1}@example.com"
        
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f"Familiar{i+1}",
                'last_name': f"Apellido{i+1}"
            }
        )
        
        if created:
            user.set_password('password123')
            user.save()
            print(f"  Creado usuario familiar: {username}")
        else:
            print(f"  Usuario familiar ya existe: {username}")
        
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'family',
                'relationship': random.choice(['Hijo/a', 'Sobrino/a', 'Nieto/a', 'Hermano/a'])
            }
        )
        
        if created:
            print(f"  Creado perfil para: {username}")
        
        # Asignar residentes aleatorios (entre 1 y 2)
        profile.related_residents.clear()  # Limpiar residentes existentes
        num_relatives = random.randint(1, 2)
        assigned_relatives = random.sample(residents, num_relatives)
        
        for relative in assigned_relatives:
            profile.related_residents.add(relative)
            
        print(f"  Familiar {username} asignado a {num_relatives} residentes")
    
    return doctors

# Función para crear dosis de medicamentos
def create_medication_doses(residents):
    print("Creando dosis de medicamentos...")
    
    # Generar fechas para los últimos 30 días
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Tiempos comunes para tomar medicamentos
    times = ['08:00', '12:00', '16:00', '20:00']
    
    for resident in residents:
        medications = resident.medications.all()
        if not medications:
            continue
        
        print(f"  Generando dosis para: {resident.name}")
        
        # Para cada medicamento del residente
        for medication in medications:
            # Determinar cuántas veces al día toma el medicamento (1 a 3)
            times_per_day = random.randint(1, 3)
            medication_times = random.sample(times, times_per_day)
            
            # Generar dosis para algunos días aleatorios
            num_days = random.randint(10, 25)  # No todos los días
            random_days = random.sample(range((end_date - start_date).days), num_days)
            
            for day_offset in random_days:
                current_date = start_date + timedelta(days=day_offset)
                
                for time_str in medication_times:
                    # Crear dosis
                    dose = f"{random.randint(1, 3)} {random.choice(['tabletas', 'cápsulas', 'ml'])}"
                    
                    MedicationDose.objects.create(
                        resident=resident,
                        medication=medication,
                        dose=dose,
                        day=current_date,
                        time=time_str,
                        medication_name=medication.name  # Assuming this field exists
                    )
    
    # Contar dosis creadas
    total_doses = MedicationDose.objects.count()
    print(f"Total de dosis creadas: {total_doses}")

# Función principal que ejecuta todas las demás
def populate_db():
    medications = create_medications()
    residents = create_residents()
    assign_medications(residents, medications)
    doctors = create_users_and_profiles(residents)
    create_medication_doses(residents)
    
    print("\nBase de datos poblada con éxito.")
    print("-------------------------------")
    print(f"Medicamentos creados: {len(medications)}")
    print(f"Residentes creados: {len(residents)}")
    print(f"Usuarios creados: {User.objects.count()}")
    print(f"Dosis registradas: {MedicationDose.objects.count()}")

# Ejecutar función principal si el script se ejecuta directamente
if __name__ == '__main__':
    print("Iniciando script para poblar la base de datos...")
    populate_db()