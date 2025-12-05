from django.db import models
from django import forms
from django.contrib.auth.hashers import make_password

# ===================================================================
# MODELO: USUARIO
# ===================================================================
class Usuario(models.Model):
# Modelo Usuario - Gestiona usuarios del sistema
# Campos:
# - nombre: Nombre completo del usuario
# - correo: Email único para login
# - contrasena: Password hasheado (usar make_password)
# - rol: Tipo de usuario (admin, visitante, otro)
# - reset_token: Token para recuperación de contraseña
# Relaciones:
# - Usado por Historial (ForeignKey)
# - Usado por Backup (ForeignKey)
# - Validado por forms.py (RegistroForm, LoginForm)

    ROL_CHOICES = [
        ('admin', 'admin'),
        ('visitante', 'visitante'),
        ('otro', 'otro'),
    ]
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(unique=True, max_length=150)
    contrasena = models.CharField(max_length=255)
    rol = models.CharField(
        max_length=20,
        choices=ROL_CHOICES,
        default='visitante'
    )
    # CORREGIDO: Agregado null=True
    reset_token = models.CharField(
        max_length=128,
        blank=True,
        null=True
    )
    class Meta:
        db_table = 'USUARIO'
    def __str__(self):
        return self.nombre

class Institucion(models.Model):
    nombre = models.CharField(max_length=150)
    ciudad = models.CharField(max_length=100, blank=True, null=True)
    pais = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'INSTITUCION'

    def __str__(self):
        return self.nombre

class Equipo(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True, blank=True, null=True)
    fecha_creacion = models.DateField(auto_now_add=True)
    institucion = models.ForeignKey(Institucion, on_delete=models.PROTECT)

    class Meta:
        db_table = 'EQUIPO'

    def __str__(self):
        return self.nombre

class Participante(models.Model):
    nombre = models.CharField(max_length=150)
    correo = models.EmailField(max_length=150)
    rol = models.CharField(max_length=50)
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)

    class Meta:
        db_table = 'PARTICIPANTE'

    def __str__(self):
        return self.nombre

class Sala(models.Model):
    nombre = models.CharField(max_length=150)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        db_table = 'SALA'

    def __str__(self):
        return self.nombre

class Ronda(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    fase = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'RONDA'

    def __str__(self):
        return self.nombre or f'Ronda {self.pk}'

class Asignacion(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE)
    posicion_equipo = models.IntegerField()

    class Meta:
        db_table = 'ASIGNACION'

    def __str__(self):
        return f"{self.equipo} @ {self.sala} ({self.ronda})"

class Puntaje(models.Model):
    participante = models.ForeignKey(Participante, on_delete=models.CASCADE)
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE)
    puntaje = models.DecimalField(max_digits=6, decimal_places=2)

    class Meta:
        db_table = 'PUNTAJE'
        unique_together = ('participante', 'sala', 'ronda')

    def __str__(self):
        return f"{self.participante}: {self.puntaje}"

class Resultado(models.Model):
    sala = models.ForeignKey(Sala, on_delete=models.CASCADE)
    ronda = models.ForeignKey(Ronda, on_delete=models.CASCADE)
    equipo_ganador = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='ganadas')
    equipo_perdedor = models.ForeignKey(Equipo, on_delete=models.CASCADE, related_name='perdidas', null=True, blank=True)

    class Meta:
        db_table = 'RESULTADO'

class Ranking(models.Model):
    equipo = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    puntajetotal = models.DecimalField(max_digits=8, decimal_places=2)
    posicion = models.IntegerField()
    class Meta:
        db_table = 'RANKING'
        ordering = ['posicion']

    def __str__(self):
        return f"{self.posicion} - {self.equipo} ({self.puntajetotal})"

class Historial(models.Model):
    fecha = models.DateTimeField()
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    cambio = models.CharField(max_length=100)
    detalle = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'HISTORIAL'

class Backup(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    fecha = models.DateTimeField()
    archivo = models.CharField(max_length=255)
    tipo = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        db_table = 'BACKUP'


