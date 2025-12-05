from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.db.models import Sum
from django.utils import timezone
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django import forms
from django.http import JsonResponse
from appTorneos.serializers import RankingSerializer, UsuarioSerializer,serializers
from .models import Equipo, Ranking, Puntaje, Ronda, Participante,Resultado,Institucion,Asignacion, Historial, Backup, Sala
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
from django.db.models import Count, Avg, Sum
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

@rol_required(['admin'])       # o el decorador que ya usas
def dashboard(request):
    puntaje_por_ronda = (
        Puntaje.objects
        .values('ronda__nombre')
        .annotate(promedio=Avg('puntaje'))
        .order_by('ronda__fecha')
    )
    labels_rondas = [str(r['ronda__nombre']) for r in puntaje_por_ronda]
    data_promedio_rondas = [float(r['promedio'] or 0) for r in puntaje_por_ronda]

    victorias_por_equipo = (
        Resultado.objects
        .values('equipo_ganador__nombre')
        .annotate(victorias=Count('id'))
        .order_by('-victorias')[:10]
    )
    labels_equipos = [str(e['equipo_ganador__nombre']) for e in victorias_por_equipo]
    data_victorias = [int(e['victorias']) for e in victorias_por_equipo]

    puntaje_total_equipo = (
        Puntaje.objects
        .values('participante__equipo__nombre')
        .annotate(total=Sum('puntaje'))
        .order_by('-total')[:10]
    )
    labels_puntaje_equipo = [str(p['participante__equipo__nombre']) for p in puntaje_total_equipo]
    data_puntaje_equipo = [float(p['total'] or 0) for p in puntaje_total_equipo]

    return render(request, "torneos/dashboard.html", {
        "labels_rondas": labels_rondas,
        "data_promedio_rondas": data_promedio_rondas,
        "labels_equipos": labels_equipos,
        "data_victorias": data_victorias,
        "labels_puntaje_equipo": labels_puntaje_equipo,
        "data_puntaje_equipo": data_puntaje_equipo,
    })
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
    
        # o el decorador que ya usas
@rol_required(['admin'])
def dashboard(request):
    promedio_por_ronda = (
        Puntaje.objects
        .values('ronda__nombre')
        .annotate(promedio=Avg('puntaje'))
        .order_by('ronda__fecha')
    )
    top_equipos = (
        Resultado.objects
        .values('equipo_ganador__nombre')
        .annotate(victorias=Count('id'))
        .order_by('-victorias')[:10]
    )
    return render(request, "torneos/dashboard.html", {
        "promedio_por_ronda": promedio_por_ronda,
        "top_equipos": top_equipos,
    })

@method_decorator(rol_required(['admin']), name='dispatch')
class InstitucionListView(ListView):
    model = Institucion
    template_name = 'instituciones/institucion_list.html'
    context_object_name = 'instituciones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class InstitucionDetailView(DetailView):
    model = Institucion
    template_name = 'instituciones/institucion_detail.html'
    context_object_name = 'institucion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class InstitucionCreateView(CreateView):
    model = Institucion
    template_name = 'instituciones/institucion_form.html'
    fields = ['nombre', 'ciudad', 'pais']
    success_url = reverse_lazy('institucion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class InstitucionUpdateView(UpdateView):
    model = Institucion
    template_name = 'instituciones/institucion_form.html'
    fields = ['nombre', 'ciudad', 'pais']
    success_url = reverse_lazy('institucion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class InstitucionDeleteView(DeleteView):
    model = Institucion
    template_name = 'instituciones/institucion_confirm_delete.html'
    success_url = reverse_lazy('institucion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ParticipanteListView(ListView):
    model = Participante
    template_name = 'participantes/participante_list.html'
    context_object_name = 'participantes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ParticipanteDetailView(DetailView):
    model = Participante
    template_name = 'participantes/participante_detail.html'
    context_object_name = 'participante'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ParticipanteCreateView(CreateView):
    model = Participante
    template_name = 'participantes/participante_form.html'
    fields = ['nombre', 'correo', 'rol', 'equipo']
    success_url = reverse_lazy('participante_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ParticipanteUpdateView(UpdateView):
    model = Participante
    template_name = 'participantes/participante_form.html'
    fields = ['nombre', 'correo', 'rol', 'equipo']
    success_url = reverse_lazy('participante_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ParticipanteDeleteView(DeleteView):
    model = Participante
    template_name = 'participantes/participante_confirm_delete.html'
    success_url = reverse_lazy('participante_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class SalaListView(ListView):
    model = Sala
    template_name = 'salas/sala_list.html'
    context_object_name = 'salas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class SalaDetailView(DetailView):
    model = Sala
    template_name = 'salas/sala_detail.html'
    context_object_name = 'sala'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class SalaCreateView(CreateView):
    model = Sala
    template_name = 'salas/sala_form.html'
    fields = ['nombre', 'tipo', 'ubicacion']
    success_url = reverse_lazy('sala_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class SalaUpdateView(UpdateView):
    model = Sala
    template_name = 'salas/sala_form.html'
    fields = ['nombre', 'tipo', 'ubicacion']
    success_url = reverse_lazy('sala_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class SalaDeleteView(DeleteView):
    model = Sala
    template_name = 'salas/sala_confirm_delete.html'
    success_url = reverse_lazy('sala_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
@method_decorator(rol_required(['admin']), name='dispatch')
class RondaListView(ListView):
    model = Ronda
    template_name = 'ronda/ronda_list.html'
    context_object_name = 'rondas'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class RondaDetailView(DetailView):
    model = Ronda
    template_name = 'ronda/ronda_detail.html'
    context_object_name = 'ronda'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class RondaCreateView(CreateView):
    model = Ronda
    template_name = 'ronda/ronda_form.html'
    fields = ['nombre', 'fecha', 'fase']
    success_url = reverse_lazy('ronda_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class RondaUpdateView(UpdateView):
    model = Ronda
    template_name = 'ronda/ronda_form.html'
    fields = ['nombre', 'fecha', 'fase']
    success_url = reverse_lazy('ronda_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class RondaDeleteView(DeleteView):
    model = Ronda
    template_name = 'ronda/ronda_confirm_delete.html'
    success_url = reverse_lazy('ronda_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@method_decorator(rol_required(['admin']), name='dispatch')
class AsignacionListView(ListView):
    model = Asignacion
    template_name = 'asignaciones/asignacion_list.html'
    context_object_name = 'asignaciones'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class AsignacionDetailView(DetailView):
    model = Asignacion
    template_name = 'asignaciones/asignacion_detail.html'
    context_object_name = 'asignacion'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class AsignacionCreateView(CreateView):
    model = Asignacion
    template_name = 'asignaciones/asignacion_form.html'
    fields = ['equipo', 'sala', 'ronda', 'posicion_equipo']
    success_url = reverse_lazy('asignacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class AsignacionUpdateView(UpdateView):
    model = Asignacion
    template_name = 'asignaciones/asignacion_form.html'
    fields = ['equipo', 'sala', 'ronda', 'posicion_equipo']
    success_url = reverse_lazy('asignacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class AsignacionDeleteView(DeleteView):
    model = Asignacion
    template_name = 'asignaciones/asignacion_confirm_delete.html'
    success_url = reverse_lazy('asignacion_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class PuntajeListView(ListView):
    model = Puntaje
    template_name = 'puntajes/puntaje_list.html'
    context_object_name = 'puntajes'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class PuntajeDetailView(DetailView):
    model = Puntaje
    template_name = 'puntajes/puntaje_detail.html'
    context_object_name = 'puntaje'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class PuntajeCreateView(CreateView):
    model = Puntaje
    template_name = 'puntajes/puntaje_form.html'
    fields = ['participante', 'sala', 'ronda', 'puntaje']
    success_url = reverse_lazy('puntaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class PuntajeUpdateView(UpdateView):
    model = Puntaje
    template_name = 'puntajes/puntaje_form.html'
    fields = ['participante', 'sala', 'ronda', 'puntaje']
    success_url = reverse_lazy('puntaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class PuntajeDeleteView(DeleteView):
    model = Puntaje
    template_name = 'puntajes/puntaje_confirm_delete.html'
    success_url = reverse_lazy('puntaje_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ResultadoListView(ListView):
    model = Resultado
    template_name = 'resultados/resultado_list.html'
    context_object_name = 'resultados'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ResultadoDetailView(DetailView):
    model = Resultado
    template_name = 'resultados/resultado_detail.html'
    context_object_name = 'resultado'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ResultadoCreateView(CreateView):
    model = Resultado
    template_name = 'resultados/resultado_form.html'
    fields = ['sala', 'ronda', 'equipo_ganador', 'equipo_perdedor']
    success_url = reverse_lazy('resultado_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ResultadoUpdateView(UpdateView):
    model = Resultado
    template_name = 'resultados/resultado_form.html'
    fields = ['sala', 'ronda', 'equipo_ganador', 'equipo_perdedor']
    success_url = reverse_lazy('resultado_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class ResultadoDeleteView(DeleteView):
    model = Resultado
    template_name = 'resultados/resultado_confirm_delete.html'
    success_url = reverse_lazy('resultado_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class HistorialListView(ListView):
    model = Historial
    template_name = 'historiales/historial_list.html'
    context_object_name = 'historiales'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class HistorialDetailView(DetailView):
    model = Historial
    template_name = 'historiales/historial_detail.html'
    context_object_name = 'historial'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class HistorialCreateView(CreateView):
    model = Historial
    template_name = 'historiales/historial_form.html'
    fields = ['fecha', 'usuario', 'cambio', 'detalle']
    success_url = reverse_lazy('historial_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class HistorialUpdateView(UpdateView):
    model = Historial
    template_name = 'historiales/historial_form.html'
    fields = ['fecha', 'usuario', 'cambio', 'detalle']
    success_url = reverse_lazy('historial_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class HistorialDeleteView(DeleteView):
    model = Historial
    template_name = 'historiales/historial_confirm_delete.html'
    success_url = reverse_lazy('historial_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class BackupListView(ListView):
    model = Backup
    template_name = 'backups/backup_list.html'
    context_object_name = 'backups'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class BackupDetailView(DetailView):
    model = Backup
    template_name = 'backups/backup_detail.html'
    context_object_name = 'backup'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class BackupCreateView(CreateView):
    model = Backup
    template_name = 'backups/backup_form.html'
    fields = ['usuario', 'fecha', 'archivo', 'tipo']
    success_url = reverse_lazy('backups_list')

    def get_context_data(self, **kwargs):    
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context


@method_decorator(rol_required(['admin']), name='dispatch')
class BackupDeleteView(DeleteView):
    model = Backup
    template_name = 'backups/backup_confirm_delete.html'
    success_url = reverse_lazy('backups_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context
    
@method_decorator(rol_required(['admin']), name='dispatch')
class BackupUpdateView(UpdateView):
    model = Backup
    template_name = 'backups/backup_form.html'
    fields = ['usuario', 'fecha', 'archivo', 'tipo']
    success_url = reverse_lazy('backups_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context