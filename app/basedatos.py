import os
import sys
import django
import random
from datetime import datetime, timedelta
from django.utils import timezone

# 1. Configurar entorno de Django
# Cambia 'hogarAbuelos.settings' a la ruta de tu archivo settings.py
# Note: Your project is named 'app', so the settings module is 'app.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.settings')
django.setup()

# 2. Importar modelos después de configurar Django
from django.contrib.auth.models import User
from residents.models import Resident
from medications.models import Medication, MedicationInventory # Import MedicationInventory
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
        except Exception as e:
            print(f"Error al buscar superusuario: {e}")


    try:
        print("Eliminando dosis de medicamentos...")
        MedicationDose.objects.all().delete()

        # Delete UserProfile objects first, linking to User and Resident
        print("Eliminando perfiles de usuario...")
        UserProfile.objects.all().delete()

        # Delete MedicationInventory before Medications
        print("Eliminando inventario de medicamentos...")
        MedicationInventory.objects.all().delete()

        print("Eliminando medicamentos...")
        Medication.objects.all().delete()

        print("Eliminando residentes...")
        Resident.objects.all().delete()

        print("Eliminando preferencias de dashboard...")
        DashboardPreference.objects.all().delete()

        print("Eliminando usuarios...")
        if preserve_superuser.lower() == 's' and superuser:
            # Delete users excluding the preserved superuser
            User.objects.exclude(id=superuser.id).delete()
        else:
            # Delete all users if superuser is not preserved or not found
            User.objects.all().delete()

        print("Base de datos limpiada con éxito.")
        return True

    except Exception as e:
        print(f"Error al limpiar la base de datos: {e}")
        return False

# -------------------------------------------------------------------
# Función para crear medicamentos de muestra y su inventario
# -------------------------------------------------------------------
def create_medications_and_inventory():
    medications = [
        'Paracetamol', 'Ibuprofeno', 'Aspirina', 'Omeprazol', 'Lorazepam',
        'Diazepam', 'Metformina', 'Enalapril', 'Losartan', 'Atorvastatina',
        'Simvastatina', 'Levotiroxina', 'Albuterol', 'Fluoxetina', 'Sertralina',
        'Esomeprazol', 'Amlodipino', 'Lisinopril', 'Metoprolol', 'Warfarina'
    ]

    print("\n=== CREANDO MEDICAMENTOS E INVENTARIO ===")
    created_medications = []

    for med_name in medications:
        medication, created = Medication.objects.get_or_create(name=med_name)
        created_medications.append(medication)
        if created:
            print(f"  ✓ Creado medicamento: {med_name}")
        else:
            print(f"  ⚠ Medicamento ya existe: {med_name}")

        # Create or update inventory for the medication
        inventory, created = MedicationInventory.objects.get_or_create(
            medication=medication,
            defaults={'quantity': random.randint(50, 200)} # Initial random quantity
        )
        if created:
            print(f"    ✓ Creado inventario para {med_name} con {inventory.quantity} unidades")
        else:
             # Update quantity if inventory already exists
             inventory.quantity = random.randint(50, 200) # Reset quantity for consistency
             inventory.save()
             print(f"    ⚠ Inventario ya existe para {med_name}, actualizado a {inventory.quantity} unidades")


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
        # Clear existing medications to avoid duplicates
        resident.medications.clear()

        # Assign between 1 and 5 random medications
        num_meds = random.randint(1, 5)
        # Ensure num_meds doesn't exceed the total number of medications
        num_meds = min(num_meds, len(medications))
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
        'administradores': [],
        'familiares': []
    }

    # Create doctors
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

        # If created, set the password
        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ Creado usuario doctor: {username}")
        else:
            print(f"  ⚠ Usuario doctor ya existe: {username}")
            # Update password to ensure consistency in tests
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
            # Ensure the user_type is correct if profile already exists
            profile.user_type = 'doctor'
            profile.specialty = profile.specialty or random.choice(['Geriatría', 'Cardiología', 'Neurología', 'Medicina Interna', 'Psiquiatría'])
            profile.save()


    # Create administrator users
    for i in range(3):
        username = f"admin{i+1}"
        email = f"admin{i+1}@example.com"

        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'email': email,
                'first_name': f"Administrador{i+1}",
                'last_name': f"Apellido{i+1}"
            }
        )

        if created:
            user.set_password(DEFAULT_PASSWORD)
            user.save()
            print(f"  ✓ Creado usuario administrador: {username}")
        else:
            print(f"  ⚠ Usuario administrador ya existe: {username}")
            user.set_password(DEFAULT_PASSWORD)
            user.save()

        created_users['administradores'].append({'username': username, 'password': DEFAULT_PASSWORD})

        profile, profile_created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'user_type': 'administrator',
                'resident': None # Admins are not typically linked to a single resident like old patients were
            }
        )

        if profile_created:
            print(f"  ✓ Creado perfil para: {username} (administrator)")
        else:
             print(f"  ⚠ Perfil ya existe para: {username}")
             profile.user_type = 'administrator'
             profile.resident = None # Ensure no old patient link persists
             profile.save()


    # Create family users
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
            # Ensure the user_type is correct if profile already exists
            profile.user_type = 'family'
            profile.relationship = profile.relationship or random.choice(['Hijo/a', 'Sobrino/a', 'Nieto/a', 'Hermano/a'])
            profile.save()


        # Assign random residents (between 1 and 2)
        profile.related_residents.clear() # Clear existing relations before adding new ones
        num_relatives = random.randint(1, 2)
        # Ensure num_relatives doesn't exceed the total number of residents
        num_relatives = min(num_relatives, len(residents))

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

        # For each medication of the resident
        for medication in medications:
            # Determine how many times a day the medication is taken (1 to 3)
            times_per_day = random.randint(1, 3)
            # Ensure times_per_day doesn't exceed the available times
            medication_times_list = random.sample(times, min(times_per_day, len(times)))

            # Generate doses for some random days
            num_days = random.randint(10, 25)  # Days with records
            total_days_range = (end_date - start_date).days
            # Ensure num_days doesn't exceed the total date range
            num_days = min(num_days, total_days_range)

            if total_days_range > 0:
                 random_day_offsets = random.sample(range(total_days_range), num_days)
            else:
                 random_day_offsets = [] # Handle case where date range is 0

            for day_offset in random_day_offsets:
                current_date = start_date + timedelta(days=day_offset)

                for time_str in medication_times_list:
                    # Create dose text, example: "1 tableta"
                    dose_text = f"{random.randint(1, 3)} {random.choice(['tabletas', 'cápsulas', 'ml'])}"
                    # Random quantity administered
                    quantity_admin = random.randint(1, 5)


                    # Check if there's enough inventory BEFORE creating
                    try:
                        inventory = medication.inventory
                        if inventory.quantity >= quantity_admin:
                             MedicationDose.objects.create(
                                resident=resident,
                                medication=medication,
                                dose=dose_text,
                                quantity_administered=quantity_admin, # Include quantity
                                day=current_date,
                                time=time_str,
                                medication_name=medication.name # This will be overwritten by model save, but good practice
                            )

                             total_doses += 1
                             resident_doses += 1
                        else:
                             # Optionally print a message if inventory is low
                             print(f"    ⊗ Inventario bajo para {medication.name}. No se creó la dosis para {resident.name} en {current_date} {time_str}")

                    except MedicationInventory.DoesNotExist:
                         print(f"    ⊗ Inventario no encontrado para {medication.name}. No se creó la dosis para {resident.name} en {current_date} {time_str}")


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

    print("\n👨‍⚕️ DOCTORES:")
    for doctor in users['doctores']:
        print(f"  Usuario: {doctor['username']:<15} | Contraseña: {doctor['password']}")

    print("\n🛡️ ADMINISTRADORES:")
    for admin in users['administradores']:
        print(f"  Usuario: {admin['username']:<15} | Contraseña: {admin['password']}")


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

    # Ask if database should be cleaned
    should_clean = input("¿Deseas limpiar la base de datos antes de poblarla? (s/n): ")
    if should_clean.lower() == 's':
        if not clean_database():
            return

    # 1. Create medications and their inventory
    medications = create_medications_and_inventory()

    # 2. Create residents
    residents = create_residents()

    # 3. Assign medications to residents
    assign_medications(residents, medications)

    # 4. Create users and profiles
    created_users = create_users_and_profiles(residents)

    # 5. Create medication dose history (this will now impact inventory)
    create_medication_doses(residents)

    # 6. Print final summary
    print("\n=== RESUMEN DE DATOS CREADOS ===")
    print(f"✓ Medicamentos: {Medication.objects.count()}")
    print(f"✓ Inventario de Medicamentos: {MedicationInventory.objects.count()}")
    print(f"✓ Residentes: {Resident.objects.count()}")
    print(f"✓ Usuarios: {User.objects.count()}")
    print(f"✓ Dosis de medicamentos: {MedicationDose.objects.count()}")

    # Show generated credentials
    print_credentials_summary(created_users)

# -------------------------------------------------------------------
# Execute main function if this file is called directly
# -------------------------------------------------------------------
if __name__ == '__main__':
    try:
        populate_db()
    except KeyboardInterrupt:
        print("\nOperación cancelada por el usuario.")
    except Exception as e:
        print(f"\nError inesperado: {e}")