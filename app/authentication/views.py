from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserLoginForm, UserSignupForm
from .models import UserProfile
from django.db import IntegrityError

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')

    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                next_url = request.GET.get('next', 'dashboard:index')
                return redirect(next_url)
            else:
                messages.error(request, 'Nombre de usuario o contraseña incorrectos.')
    else:
        form = UserLoginForm()

    return render(request, 'authentication/login.html', {'form': form})

# @login_required # You might want to restrict signup to authenticated users (e.g., administrators)
def signup_view(request):
    # Allow superusers or administrators to access signup page
    if request.user.is_authenticated:
        if not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_administrator())):
             return redirect('dashboard:index') # Redirect if not authorized
    elif request.user.is_authenticated: # If authenticated but not superuser/admin
         return redirect('dashboard:index') # Redirect if not authorized


    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            # If you decide to associate an administrator with ONE resident for dashboard view:
            selected_resident_for_admin = form.cleaned_data.get('resident')
            if form.cleaned_data.get('user_type') == 'administrator' and selected_resident_for_admin:
                 if UserProfile.objects.filter(user_type='administrator', resident=selected_resident_for_admin).exists():
                     messages.error(request, f'El residente {selected_resident_for_admin.name} ya está asignado a otro usuario administrador. Por favor, seleccione otro residente o contacte al administrador.')
                     return render(request, 'authentication/signup.html', {'form': form})

            try:
                # Create the user
                user = form.save(commit=False) # Don't save profile yet
                user.save()

                # User profile creation is now handled in the form's save method
                # The form's save method creates/updates the UserProfile and sets role-specific fields.
                form.save()

                # Don't auto-login newly created users here if only admins create users
                # Instead, redirect to a success page or the dashboard
                messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
                return redirect('dashboard:index') # Redirect to dashboard after creating user

            except IntegrityError as e:
                if 'UNIQUE constraint failed: authentication_userprofile.resident_id' in str(e):
                    messages.error(request, 'Este residente ya está asignado a otro usuario. Por favor, seleccione otro residente.')
                else:
                    messages.error(request, f'Error al crear el usuario: {str(e)}')

                # If an error occurs, try to delete the user that was just created
                if 'user' in locals() and user.pk:
                    user.delete()

                return render(request, 'authentication/signup.html', {'form': form})
    else:
        form = UserSignupForm()

    return render(request, 'authentication/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('authentication:login')

# This view seems redundant with signup_view. You likely only need one.
# Assuming this is just an alias for the signup view logic.
def create_user(request):
    # Restrict this view to administrators and superusers
    if not request.user.is_authenticated or not (request.user.is_superuser or (hasattr(request.user, 'profile') and request.user.profile.is_administrator())):
         return redirect('dashboard:index') # Redirect if not authorized

    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
             # If you decide to associate an administrator with ONE resident for dashboard view:
            selected_resident_for_admin = form.cleaned_data.get('resident')
            if form.cleaned_data.get('user_type') == 'administrator' and selected_resident_for_admin:
                 if UserProfile.objects.filter(user_type='administrator', resident=selected_resident_for_admin).exists():
                     messages.error(request, f'El residente {selected_resident_for_admin.name} ya está asignado a otro usuario administrador. Por favor, seleccione otro residente o contacte al administrador.')
                     return render(request, 'authentication/signup.html', {'form': form})


            try:
                # Create the user
                user = form.save(commit=False)
                user.save()

                # User profile creation is now handled in the form's save method
                form.save()

                messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
                return redirect('dashboard:index')

            except IntegrityError as e:
                 if 'UNIQUE constraint failed: authentication_userprofile.resident_id' in str(e):
                     messages.error(request, 'Este residente ya está asignado a otro usuario. Por favor, seleccione otro residente.')
                 else:
                     messages.error(request, f'Error al crear el usuario: {str(e)}')

                 # If an error occurs, try to delete the user that was just created
                 if 'user' in locals() and user.pk:
                     user.delete()

                 return render(request, 'authentication/signup.html', {'form': form})
    else:
        form = UserSignupForm()

    # Assuming you want to use the signup template for this view as well
    return render(request, 'authentication/signup.html', {'form': form})