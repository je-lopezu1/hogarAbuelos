import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# 1. Configurar entorno de Django
# Cambia 'hogarAbuelos.settings' a la ruta de tu archivo settings.py
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

# 2. Importar modelos después de configurar Django
from django.contrib.auth.models import User
from residents.models import Resident
from medications.models import Medication
from medication_dose.models import MedicationDose
from authentication.models import UserProfile
from dashboard.models import DashboardPreference

# Contraseña estándar para facilitar las pruebas
DEFAULT_PASSWORD = 'password123'

# -------------------------------------------------------------------
# Función para limpiar la base de datos antes de repoblarla
# -------------------------------------------------------------------
def clean_database():
    print("\n=== LIMPIANDO BASE DE DATOS ===")
    print("¡ATENCIÓN! Esto eliminará todos los datos existentes.")
    confirm = input("¿Estás seguro de que deseas continuar? (s/n): ")

    if confirm.lower() != 's':
        print("Operación cancelada.")
        return False

    # Guardar el superusuario antes de eliminar todo
    preserve_superuser = input("¿Preservar el superusuario? (s/n): ")
    superuser = None

    if preserve_superuser.lower() == 's':
        try:
            superuser = User.objects.filter(is_superuser=True).first()
            if superuser:
                print(f"Se preservará el superusuario: {superuser.username}")
        except:
            print("No se encontró ningún superusuario.")

    try:
        print("Eliminando dosis de medicamentos...")
        MedicationDose.objects.all().delete()

        print("Eliminando perfiles de usuario...")
        UserProfile.objects.all().delete()

        print("Eliminando medicamentos...")
        Medication.objects.all().delete()

        print("Eliminando residentes...")
        Resident.objects.all().delete()

        print("Eliminando preferencias de dashboard...")
        DashboardPreference.objects.all().delete()

        print("Eliminando usuarios...")
        if preserve_superuser.lower() == 's' and superuser:
            User.objects.exclude(id=superuser.id).delete()
        else:
            User.objects.all().delete()

        print("Base de datos limpiada con éxito.")
        return True

    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
        return False

# -------------------------------------------------------------------
# Función para crear medicamentos de muestra
# -------------------------------------------------------------------
def create_medications():
    medications = [
        'Paracetamol', 'Ibuprofeno', 'Aspirina', 'Omeprazol', 'Lorazepam',
        'Diazepam', 'Metformina', 'Enalapril', 'Losartan', 'Atorvastatina',
        'Simvastatina', 'Levotiroxina', 'Albuterol', 'Fluoxetina', 'Sertralina',
        'Esomeprazol', 'Amlodipino', 'Lisinopril', 'Metoprolol', 'Warfarina'
    ]

    print("\n=== CREANDO MEDICAMENTOS ===")
    created_medications = []

    for med_name in medications:
        medication, created = Medication.objects.get_or_create(name=med_name)
        created_medications.append(medication)
        if created:
            print(f"  ✓ Creado medicamento: {med_name}")
        else:
            print(f"  ⚠ Medicamento ya existe: {med_name}")

    return created_medications

# -------------------------------------------------------------------
# Función para crear residentes de muestra
# -------------------------------------------------------------------
def create_residents():
    first_names = [
        'María', 'José', 'Antonio', 'Carmen', 'Juan', 'Ana', 'Francisco',
        'Isabel', 'Manuel', 'Dolores', 'Luis', 'Pilar', 'Miguel', 'Teresa',
        'Carlos', 'Elena'
    ]

    last_names = [
        'García', 'Rodríguez', 'González', 'Fernández', 'López', 'Martínez',
        'Sánchez', 'Pérez', 'Gómez', 'Martín', 'Jiménez', 'Ruiz',
        'Hernández', 'Díaz', 'Moreno'
    ]

    medical_conditions = [
        'Hipertensión arterial', 'Diabetes mellitus tipo 2', 'Artritis',
        'Parkinson', 'Alzheimer leve', 'Insuficiencia cardíaca', 'EPOC',
        'Osteoporosis', 'Cataratas', 'Artrosis', 'Depresión', 'Ansiedad',
        'Hipotiroidismo', 'Fibrilación auricular', 'Enfermedad renal crónica'
    ]

    print("\n=== CREANDO RESIDENTES ===")
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
            print(f"  ✓ Creado residente: {name}, {age} años, {condition}")
        else:
            print(f"  ⚠ Residente ya existe: {name}")

    return created_residents

# -------------------------------------------------------------------
# Función para asignar medicamentos aleatorios a los residentes
# -------------------------------------------------------------------
def assign_medications(residents, medications):
    print("\n=== ASIGNANDO MEDICAMENTOS A RESIDENTES ===")

    for resident in residents:
        # Limpiar medicamentos existentes para evitar duplicados
        resident.medications.clear()

        # Asignar entre 1 y 5 medicamentos aleatorios
        num_meds = random.randint(1, 5)
        selected_meds = random.sample(medications, num_meds)

        for med in selected_meds:
            resident.medications.add(med)

        meds_list = ", ".join([med.name for med in selected_meds])
        print(f"  ✓ {resident.name} recibe {num_meds} medicamentos: {meds_list}")

    return residents

# -------------------------------------------------------------------
# Función para crear usuarios y perfiles
# -------------------------------------------------------------------
def create_users_and_profiles(residents):
    print("\n=== CREANDO USUARIOS Y PERFILES ===")
    print(f"Contraseña para todos los usuarios: {DEFAULT_PASSWORD}")

    created_users = {
        'doctores': [],
        'pacientes': [],
        'familiares': []
    }

    # Crear médicos (doctors)
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

        # Si se creó, establecer la contraseña
        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ Creado usuario doctor: {username}")
        else:
            print(f"  ⚠ Usuario doctor ya existe: {username}")
            # Actualizar contraseña para asegurar consistencia en pruebas
            user.set_password(DEFAULT_PASSWORD)
            user.save()

        created_users['doctores'].append({'username': username, 'password': DEFAULT_PASSWORD})

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'doctor',
                'specialty': random.choice(['Geriatría', 'Cardiología', 'Neurología', 'Medicina Interna', 'Psiquiatría'])
            }
        )

        if profile_created:
            print(f"  ✓ Creado perfil para: {username} (doctor)")
        else:
            print(f"  ⚠ Perfil ya existe para: {username}")
            # Nos aseguramos de que sea 'doctor'
            profile.user_type = 'doctor'
            profile.specialty = random.choice(['Geriatría', 'Cardiología', 'Neurología', 'Medicina Interna', 'Psiquiatría'])
            profile.save()


    # Crear usuarios "paciente" para algunos residentes
    for i, resident in enumerate(residents[:10]):  # Solo para los primeros 10 residentes
        username = f"paciente{i+1}"
        email = f"paciente{i+1}@example.com"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': resident.name.split()[0],
                'last_name': " ".join(resident.name.split()[1:]) if len(resident.name.split()) > 1 else ""
            }
        )

        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ Creado usuario paciente: {username}")
        else:
            print(f"  ⚠ Usuario paciente ya existe: {username}")
            user.set_password(DEFAULT_PASSWORD)
            user.save()

        created_users['pacientes'].append({'username': username, 'password': DEFAULT_PASSWORD})

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'patient',
                'resident': resident
            }
        )

        if profile_created:
            print(f"  ✓ Creado perfil para: {username} (patient), asociado a {resident.name}")
        else:
            # Asegurar que el perfil está asociado al residente correcto
            profile.user_type = 'patient'
            profile.resident = resident
            profile.save()
            print(f"  ⚠ Perfil actualizado para: {username}, asociado a residente: {resident.name}")

    # Crear usuarios "familiar"
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
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ Creado usuario familiar: {username}")
        else:
            print(f"  ⚠ Usuario familiar ya existe: {username}")
            user.set_password(DEFAULT_PASSWORD)
            user.save()

        created_users['familiares'].append({'username': username, 'password': DEFAULT_PASSWORD})

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'family',
                'relationship': random.choice(['Hijo/a', 'Sobrino/a', 'Nieto/a', 'Hermano/a'])
            }
        )

        if profile_created:
            print(f"  ✓ Creado perfil para: {username} (family)")
        else:
            print(f"  ⚠ Perfil ya existe para: {username}")
            profile.user_type = 'family'
            profile.relationship = random.choice(['Hijo/a', 'Sobrino/a', 'Nieto/a', 'Hermano/a'])
            profile.save()

        # Asignar residentes aleatorios (entre 1 y 2)
        profile.related_residents.clear()
        num_relatives = random.randint(1, 2)
        assigned_relatives = random.sample(residents, num_relatives)

        for relative in assigned_relatives:
            profile.related_residents.add(relative)

        relatives_list = ", ".join([relative.name for relative in assigned_relatives])
        print(f"  ✓ Familiar {username} asignado a {num_relatives} residentes: {relatives_list}")

    return created_users

# -------------------------------------------------------------------
# Función para crear dosis de medicamentos
# -------------------------------------------------------------------
def create_medication_doses(residents):
    print("\n=== CREANDO DOSIS DE MEDICAMENTOS ===")

    # Generar fechas para los últimos 30 días
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)

    # Tiempos comunes para tomar medicamentos
    times = ['08:00', '12:00', '16:00', '20:00']

    total_doses = 0

    for resident in residents:
        medications = resident.medications.all()
        if not medications:
            continue

        print(f"  Generando dosis para: {resident.name}")
        resident_doses = 0

        # Para cada medicamento del residente
        for medication in medications:
            # Determinar cuántas veces al día toma el medicamento (1 a 3)
            times_per_day = random.randint(1, 3)
            medication_times = random.sample(times, times_per_day)

            # Generar dosis para algunos días aleatorios
            num_days = random.randint(10, 25)  # Días con registro
            random_days = random.sample(range((end_date - start_date).days), num_days)

            for day_offset in random_days:
                current_date = start_date + timedelta(days=day_offset)

                for time_str in medication_times:
                    # Crear dosis, ejemplo: "1 tabletas"
                    dose_text = f"{random.randint(1, 3)} {random.choice(['tabletas', 'cápsulas', 'ml'])}"

                    MedicationDose.objects.create(
                        resident=resident,
                        medication=medication,
                        dose=dose_text,
                        day=current_date,
                        time=time_str,
                        medication_name=medication.name
                    )

                    total_doses += 1
                    resident_doses += 1

        print(f"    ✓ {resident_doses} dosis creadas para {resident.name}")

    print(f"\nTotal de dosis creadas: {total_doses}")

# -------------------------------------------------------------------
# Imprimir resumen de credenciales
# -------------------------------------------------------------------
def print_credentials_summary(users):
    print("\n========================================================")
    print("              RESUMEN DE CREDENCIALES")
    print("========================================================")
    print(f"Contraseña universal: {DEFAULT_PASSWORD}")
    print("--------------------------------------------------------")

    print("\n👨‍⚕️ MÉDICOS:")
    for doctor in users['doctores']:
        print(f"  Usuario: {doctor['username']:<15} | Contraseña: {doctor['password']}")

    print("\n👴 PACIENTES:")
    for patient in users['pacientes']:
        print(f"  Usuario: {patient['username']:<15} | Contraseña: {patient['password']}")

    print("\n👪 FAMILIARES:")
    for family in users['familiares']:
        print(f"  Usuario: {family['username']:<15} | Contraseña: {family['password']}")

    print("\n========================================================")
    print("¡Base de datos poblada con éxito!")
    print("Utiliza estas credenciales para iniciar sesión en el sistema.")
    print("========================================================")

# -------------------------------------------------------------------
# Función principal
# -------------------------------------------------------------------
def populate_db():
    print("\n============================================")
    print("   SCRIPT DE GENERACIÓN DE DATOS FICTICIOS")
    print("============================================")

    # Preguntar si se desea limpiar la base de datos
    should_clean = input("¿Deseas limpiar la base de datos antes de poblarla? (s/n): ")
    if should_clean.lower() == 's':
        if not clean_database():
            return

    # 1. Crear medicamentos
    medications = create_medications()

    # 2. Crear residentes
    residents = create_residents()

    # 3. Asignar medicamentos a residentes
    assign_medications(residents, medications)

    # 4. Crear usuarios y perfiles
    created_users = create_users_and_profiles(residents)

    # 5. Crear historial de dosis de medicamentos
    create_medication_doses(residents)

    # 6. Imprimir resumen final
    print("\n=== RESUMEN DE DATOS CREADOS ===")
    print(f"✓ Medicamentos: {Medication.objects.count()}")
    print(f"✓ Residentes: {Resident.objects.count()}")
    print(f"✓ Usuarios: {User.objects.count()}")
    print(f"✓ Dosis de medicamentos: {MedicationDose.objects.count()}")

    # Mostrar credenciales generadas
    print_credentials_summary(created_users)

# -------------------------------------------------------------------
# Ejecutar función principal si se llama directamente este archivo
# -------------------------------------------------------------------
if __name__ == '__main__':
    try:
        populate_db()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")