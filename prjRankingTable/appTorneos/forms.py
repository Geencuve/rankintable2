from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password

class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(widget=forms.PasswordInput)
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contrasena', 'rol']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("contrasena")
        confirm = cleaned_data.get("confirmar_contrasena")
        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        cleaned_data["contrasena"] = make_password(password)
        return cleaned_data


class LoginForm(forms.Form):
    correo = forms.EmailField(label="Correo")
    contrasena = forms.CharField(widget=forms.PasswordInput, label="Contraseña")
