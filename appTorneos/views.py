from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django import forms
from django.http import JsonResponse
from appTorneos.serializers import RankingSerializer, UsuarioSerializer,serializers
from .models import Equipo, Ranking, Puntaje, Sala, Ronda, Participante,Resultado
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from .views_auth import rol_required
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Usuario
from django.contrib import messages
from .forms import RegistroForm
from .views_auth import rol_required
from django.contrib.auth.hashers import make_password

@api_view(['GET', 'PUT', 'DELETE'])
def usuario_api_detail(request, pk):
    try:
        usuario = Usuario.objects.get(pk=pk)
    except Usuario.DoesNotExist:
        return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = UsuarioSerializer(usuario)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = UsuarioSerializer(usuario, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        usuario.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)




@rol_required(['admin'])
def usuarios_list(request):
    usuarios = Usuario.objects.all()
    return render(request, 'usuarios/usuarios_list.html', {'usuarios': usuarios})

class UsuarioListView(ListView):
    model = Usuario
    template_name = 'usuarios/usuario_list.html'
    context_object_name = 'usuarios'

class UsuarioCreateView(CreateView):
    model = Usuario
    fields = ['nombre', 'correo', 'contrasena', 'rol']
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

class UsuarioUpdateView(UpdateView):
    model = Usuario
    fields = ['nombre', 'correo', 'contrasena', 'rol']
    template_name = 'usuarios/usuario_form.html'
    success_url = reverse_lazy('usuario_list')

class UsuarioDeleteView(DeleteView):
    model = Usuario
    template_name = 'usuarios/usuario_confirm_delete.html'
    success_url = reverse_lazy('usuario_list')

@rol_required(['admin'])
def registrar_usuario(request):
    # Solo admin puede registrar, y requiere código de validación "dbsmanager"
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        codigo_validacion = request.POST.get('codigo_validacion', '')
        if codigo_validacion != 'dbsmanager':
            messages.error(request, "Código de validación incorrecto.")
            return render(request, 'usuarios/registrar_usuario.html', {'form': form})
        if form.is_valid():
            form.save()
            messages.success(request, "Usuario registrado exitosamente.")
            return redirect('usuarios_list')
    else:
        form = RegistroForm()
    return render(request, 'usuarios/registrar_usuario.html', {'form': form})

@rol_required(['admin'])
def dashboard(request):
        return render(request, 'torneos/dashboard.html')


# --- Vista JsonResponse Views---
@api_view(['GET', 'POST'])
@rol_required(['admin'])
def ranking_list(request):
    if request.method == 'GET':
        rankings = Ranking.objects.all()
        serializer = RankingSerializer(rankings, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = RankingSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@rol_required(['admin'])
def ranking_detail(request,pk):
    try:
        ranking = Ranking.objects.get(pk=pk)
    except Ranking.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = RankingSerializer(ranking)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = RankingSerializer(ranking, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        ranking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

def posisionamientosviews(request):
    posicion = Ranking.objects.all()
    data={'Posicion':list(posicion.values('posicion', 'equipo_id', 'puntajetotal'))}
    return JsonResponse (data)

# --- Vista de la tabla de posicionamiento ---
def tabla_posicionamiento(request):
    rankings = Ranking.objects.select_related('equipo').order_by('posicion')
    if rankings.exists():
        tabla = [{
            'posicion': r.posicion,
            'equipo': r.equipo,
            'puntajetotal': r.puntajetotal,
            'pj': None, 'g': None, 'e': None, 'p': None, 'gf': None, 'gc': None, 'dg': None,
        } for r in rankings]
        autocalc = False
    else:
        qs = (Puntaje.objects
              .select_related('participante__equipo')
              .values('participante__equipo')
              .annotate(puntajetotal=Sum('puntaje'))
              .order_by('-puntajetotal'))
        tabla = []
        for idx, row in enumerate(qs, start=1):
            equipo_id = row['participante__equipo']
            try:
                equipo = Equipo.objects.get(pk=equipo_id)
            except Equipo.DoesNotExist:
                continue
            tabla.append({
                'posicion': idx,
                'equipo': equipo,
                'puntajetotal': row['puntajetotal'] or 0,
                'pj': None, 'g': None, 'e': None, 'p': None, 'gf': None, 'gc': None, 'dg': None,
            })
        autocalc = True

    context = {
        'tabla': tabla,
        'autocalc': autocalc,
        'now': timezone.now(),
    }
    return render(request, 'torneos/tabla_posicionamiento.html', context)

# --- Vista de inicio (top 3 destacados) ---
def inicio(request):
    destacados = Ranking.objects.select_related('equipo').order_by('posicion')[:3]
    tabla = [{
        'posicion': r.posicion,
        'equipo': r.equipo,
        'puntajetotal': r.puntajetotal,
    } for r in Ranking.objects.select_related('equipo').order_by('posicion')]
    context = {
        'now': timezone.now(),
        'destacados': destacados,
        'tabla': tabla,
    }
    return render(request, 'inicio.html', context)

# --- Vistas de CRUD para Equipo ---

@method_decorator(rol_required(['admin']), name='dispatch')
class EquipoListView(ListView):
    model = Equipo
    template_name = 'torneos/equipo_list.html'
    context_object_name = 'equipos'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class EquipoDetailView(DetailView):
    model = Equipo
    template_name = 'torneos/equipo_detail.html'
    context_object_name = 'equipo'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class EquipoCreateView(CreateView):
    model = Equipo
    template_name = 'torneos/equipo_form.html'
    fields = ['nombre', 'codigo', 'institucion']
    success_url = reverse_lazy('equipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class EquipoUpdateView(UpdateView):
    model = Equipo
    template_name = 'torneos/equipo_form.html'
    fields = ['nombre', 'codigo', 'institucion']
    success_url = reverse_lazy('equipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class EquipoDeleteView(DeleteView):
    model = Equipo
    template_name = 'torneos/equipo_confirm_delete.html'
    success_url = reverse_lazy('equipo_list')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

# --- CRUD para Ranking ---
@method_decorator(rol_required(['admin']), name='dispatch')
class RankingCreateView(CreateView):
    model = Ranking
    template_name = 'torneos/ranking_form.html'
    fields = ['equipo', 'puntajetotal', 'posicion']
    success_url = reverse_lazy('tabla_posicionamiento')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class RankingUpdateView(UpdateView):
    model = Ranking
    template_name = 'torneos/ranking_form.html'
    fields = ['equipo', 'puntajetotal', 'posicion']
    success_url = reverse_lazy('tabla_posicionamiento')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
@method_decorator(rol_required(['admin']), name='dispatch')
class RankingDeleteView(DeleteView):
    model = Ranking
    template_name = 'torneos/ranking_confirm_delete.html'
    success_url = reverse_lazy('tabla_posicionamiento')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
@method_decorator(rol_required(['admin']), name='dispatch')
class RankingListView(ListView):
    model = Ranking
    template_name = 'torneos/ranking_list.html'
    context_object_name = 'rankings'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

# --- Formulario y vista para agregar puntaje ---
@rol_required(['admin'])
class PuntajeEquipoForm(forms.ModelForm):
    class Meta:
        model = Puntaje
        fields = ['participante', 'sala', 'ronda', 'puntaje']

@rol_required(['admin'])
def agregar_puntaje(request, equipo_id):
    equipo = get_object_or_404(Equipo, pk=equipo_id)
    form = PuntajeEquipoForm()
    form.fields['participante'].queryset = Participante.objects.filter(equipo=equipo)
    if request.method == 'POST':
        form = PuntajeEquipoForm(request.POST)
        form.fields['participante'].queryset = Participante.objects.filter(equipo=equipo)
        if form.is_valid():
            form.save()
            return redirect('equipo_list')
    return render(request, 'torneos/agregar_puntaje.html', {'form': form, 'equipo': equipo, 'now': timezone.now()})



def matriz_enfrentamientos(request):
    equipos = list(Equipo.objects.all())
    matriz_resultados = {e.pk: {} for e in equipos}
    for res in Resultado.objects.all():
        matriz_resultados[res.equipo_ganador.pk][res.equipo_perdedor.pk] = 'G'
        matriz_resultados[res.equipo_perdedor.pk][res.equipo_ganador.pk] = 'P'
    # Si tienes empates, añade 'E' en ambas direcciones
    context = {
        'equipos': equipos,
        'matriz_resultados': matriz_resultados,
    }
    return render(request, 'torneos/matriz_enfrentamientos.html', context)

def tabla_eliminacion_directa(request):
    rondas = Ronda.objects.values_list('fase', flat=True).distinct()
    rondas_resultados = {}
    for ronda in rondas:
        resultados = Resultado.objects.filter(ronda__fase=ronda)
        rondas_resultados[ronda] = resultados
    context = {
        'rondas_resultados': rondas_resultados,
    }
    return render(request, 'torneos/tabla_eliminacion_directa.html', context)



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