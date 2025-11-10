
# ===================================================================
# SERIALIZERS.PY - Serializadores para la API REST
# ===================================================================
# Este archivo contiene los serializadores que convierten los modelos
# Django a formato JSON y viceversa para la API REST
# ===================================================================
# CORREGIDO: Importación correcta desde rest_framework
from rest_framework import serializers
from appTorneos.models import Ranking, Usuario
from django.contrib.auth.hashers import make_password
class RankingSerializer(serializers.ModelSerializer):
    
# Serializador para el modelo Ranking.
# Funciones:
# - Serialización: Convierte objetos Ranking a JSON
# - Deserialización: Convierte JSON a objetos Ranking
# - Validación: Valida datos según modelo
# Relaciones:
# - Usado en views.py (ranking_list, ranking_detail)
# - Trabaja con modelo Ranking de models.py

    class Meta:
        model = Ranking
        fields = '__all__'
# Campos: id, equipo, puntajetotal, posicion


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ['id', 'nombre', 'correo', 'contrasena', 'rol']
        extra_kwargs = {'contrasena': {'write_only': True}}

    def create(self, validated_data):
        validated_data['contrasena'] = make_password(validated_data['contrasena'])
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if 'contrasena' in validated_data:
            validated_data['contrasena'] = make_password(validated_data['contrasena'])
        return super().update(instance, validated_data)