from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserLoginForm, UserSignupForm
from .models import UserProfile

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

def signup_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard:index')
        
    if request.method == 'POST':
        form = UserSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Obtener o actualizar el perfil de usuario
            # La señal post_save ya debería haber creado el perfil
            try:
                user_profile = UserProfile.objects.get(user=user)
            except UserProfile.DoesNotExist:
                # En caso de que no exista, crearlo
                user_profile = UserProfile(user=user)
            
            # Actualizar campos del perfil
            user_profile.user_type = form.cleaned_data.get('user_type')
            user_profile.phone_number = form.cleaned_data.get('phone_number')
            
            # Agregar campos específicos según el tipo de usuario
            if user_profile.user_type == 'doctor':
                user_profile.specialty = form.cleaned_data.get('specialty')
                user_profile.save()  # Guardar antes de establecer relaciones many-to-many
                if form.cleaned_data.get('patients'):
                    user_profile.patients.set(form.cleaned_data.get('patients'))
            
            elif user_profile.user_type == 'patient':
                if form.cleaned_data.get('resident'):
                    user_profile.resident = form.cleaned_data.get('resident')
                user_profile.save()
            
            elif user_profile.user_type == 'family':
                user_profile.relationship = form.cleaned_data.get('relationship')
                user_profile.save()  # Guardar antes de establecer relaciones many-to-many
                if form.cleaned_data.get('related_residents'):
                    user_profile.related_residents.set(form.cleaned_data.get('related_residents'))
            
            # Guardar el perfil
            user_profile.save()
            
            # Iniciar sesión del usuario
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=user.username, password=raw_password)
            login(request, user)
            return redirect('dashboard:index')
    else:
        form = UserSignupForm()
    
    return render(request, 'authentication/signup.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('authentication:login')