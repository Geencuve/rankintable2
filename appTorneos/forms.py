from django import forms
from .models import Usuario
from django.contrib.auth.hashers import make_password, check_password

class RegistroForm(forms.ModelForm):
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmar_contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    nombre = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    rol = forms.ChoiceField(
        choices=[('admin', 'admin')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Usuario
        fields = ['nombre', 'correo', 'contrasena', 'rol']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('contrasena')
        confirm = cleaned_data.get('confirmar_contrasena')
        if password != confirm:
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('contrasena')
        if password:
            user.contrasena = make_password(password)
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    correo = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    contrasena = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class PasswordResetRequestForm(forms.Form):
    correo = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

class SetPasswordForm(forms.Form):
    nueva_contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    confirmar_contrasena = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cd = super().clean()
        if cd.get('nueva_contrasena') != cd.get('confirmar_contrasena'):
            raise forms.ValidationError("Las contraseñas no coinciden")
        return cd


