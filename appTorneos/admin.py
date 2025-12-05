from django.contrib import admin
from .models import Usuario, Institucion, Equipo, Participante, Sala, Ronda, Asignacion, Puntaje, Resultado, Ranking, Historial, Backup

admin.site.register([Usuario, Institucion, Equipo, Participante, Sala, Ronda, Asignacion, Puntaje, Resultado, Ranking, Historial, Backup])
