import os
import shutil
import subprocess
import sys

def reset_migrations():
    """
    Deletes all migration files (except __init__.py) in all apps' migrations folders
    and then runs makemigrations.
    Designed for use in a development environment.
    """
    project_root = os.path.dirname(os.path.abspath(__file__))
    print(f"Project root: {project_root}")

    migrations_deleted_count = 0

    for root, dirs, files in os.walk(project_root):
        if 'migrations' in dirs:
            migrations_dir = os.path.join(root, 'migrations')
            if os.path.isdir(migrations_dir):
                print(f"Found migrations directory: {migrations_dir}")
                for filename in os.listdir(migrations_dir):
                    filepath = os.path.join(migrations_dir, filename)
                    if os.path.isfile(filepath) and filename.endswith('.py') and filename != '__init__.py':
                        try:
                            os.remove(filepath)
                            print(f"  Deleted: {filename}")
                            migrations_deleted_count += 1
                        except OSError as e:
                            print(f"  Error deleting {filename}: {e}")

    print(f"\nDeleted {migrations_deleted_count} migration files.")

    # Run makemigrations
    print("\nRunning 'python manage.py makemigrations'...")
    try:
        subprocess.run([sys.executable, 'manage.py', 'makemigrations'], check=True)
        print("\n'makemigrations' completed successfully.")
    except subprocess.CalledProcessError as e:
        print(f"\nError running 'makemigrations': {e}")
        print("Please review the output and fix any errors.")

if __name__ == '__main__':
    confirm = input("WARNING: This script will delete all migration files (except __init__.py).\nThis is for DEVELOPMENT ONLY and can cause data loss if used incorrectly.\nAre you sure you want to continue? (yes/no): ")
    if confirm.lower() == 'yes':
        reset_migrations()
        print("\nMigration reset process finished.")
        print("Remember to run 'python manage.py migrate' afterwards to apply the new migrations.")
        print("You might also need to run your data population script if you started with an empty database.")
    else:
        print("Operation cancelled.")