from django.shortcuts import render, redirect
from .forms import RegistroForm, LoginForm, PasswordResetRequestForm, SetPasswordForm
from .models import Usuario
from django.contrib import messages
from django.contrib.auth.hashers import check_password, make_password
from functools import wraps
import secrets
from django.urls import reverse

# Decorador rol_required para validar roles
def rol_required(roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_rol = request.session.get('user_rol')
            if user_rol not in roles:
                messages.error(request, "No tienes permisos para acceder")
                return redirect('login')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Registro solo para administradores con validación de código

def registro_view(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        codigo_validacion = request.POST.get('codigo_validacion', '')
        if codigo_validacion != 'dbsmanager':
            messages.error(request, "Código de validación incorrecto.")
            return render(request, 'auth/registro.html', {'form': form})
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado exitosamente")
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'auth/registro.html', {'form': form})

# Login view sin cambios
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            correo = form.cleaned_data['correo']
            contrasena = form.cleaned_data['contrasena']
            try:
                user = Usuario.objects.get(correo=correo)
                if check_password(contrasena, user.contrasena):
                    request.session['user_id'] = user.id
                    request.session['user_rol'] = user.rol
                    messages.success(request, f"Bienvenido {user.nombre}")
                    return redirect('dashboard')
                else:
                    messages.error(request, "Contraseña incorrecta")
            except Usuario.DoesNotExist:
                messages.error(request, "Credenciales incorrectas")
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})

# Logout limpio
def logout_view(request):
    request.session.flush()
    messages.success(request, "Sesión cerrada exitosamente")
    return redirect('login')

# Solicitar recuperación de contraseña
def password_reset_request(request):
    form = None
    mensaje_enviado = False

    if request.method == 'POST':
        form = PasswordResetRequestForm(request.POST)
        if form and form.is_valid():
            correo = form.cleaned_data['correo']
            try:
                user = Usuario.objects.get(correo=correo)
                user.reset_token = secrets.token_urlsafe(32)
                user.save()
                reset_url = request.build_absolute_uri(
                    reverse('set_password', args=[user.reset_token])
                )
                return redirect(reset_url)
            except Usuario.DoesNotExist:
                pass
            mensaje_enviado = True
    else:
        form = PasswordResetRequestForm()
    return render(request, 'auth/password_reset_request.html',
                  {'form': form, 'mensaje_enviado': mensaje_enviado})

# Cambiar contraseña con token
def set_password(request, token):
    try:
        user = Usuario.objects.get(reset_token=token)
    except Usuario.DoesNotExist:
        user = None
    if not user:
        return render(request, 'auth/password_reset_invalid.html')

    if request.method == 'POST':
        form = SetPasswordForm(request.POST)
        if form.is_valid():
            user.contrasena = make_password(form.cleaned_data['nueva_contrasena'])
            user.reset_token = ''
            user.save()
            messages.success(request, "Contraseña actualizada")
            return redirect('login')
    else:
        form = SetPasswordForm()
    return render(request, 'auth/set_password.html', {'form': form})
