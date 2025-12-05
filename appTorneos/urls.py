from django.urls import path
from . import views
from .views_auth import login_view, registro_view, logout_view
from . import views_auth
from .views import (UsuarioUpdateView, UsuarioDeleteView, UsuarioListView,UsuarioCreateView,usuario_api_detail, 
                     InstitucionListView, InstitucionCreateView,InstitucionUpdateView,  InstitucionDeleteView, InstitucionDetailView, 
                     ParticipanteCreateView, ParticipanteListView, ParticipanteUpdateView, ParticipanteDeleteView, ParticipanteDetailView,
                     PuntajeCreateView, PuntajeListView, PuntajeUpdateView, PuntajeDeleteView, PuntajeDetailView,
                     BackupListView, BackupCreateView, BackupDetailView, BackupUpdateView, BackupDeleteView, 
                     SalaListView, SalaCreateView, SalaUpdateView, SalaDeleteView, SalaDetailView,
                     ResultadoListView, ResultadoCreateView, ResultadoUpdateView, ResultadoDeleteView, ResultadoDetailView,
                     RondaListView, RondaCreateView, RondaUpdateView, RondaDeleteView, RondaDetailView)



urlpatterns = [
    path('', views.inicio, name='home'),
    path('tabla/', views.tabla_posicionamiento, name='tabla_posicionamiento'),
    path('inicio/', views.inicio, name='inicio'),
    # CRUD Equipo
    path('equipos/', views.EquipoListView.as_view(), name='equipo_list'),
    path('equipos/nuevo/', views.EquipoCreateView.as_view(), name='equipo_create'),
    path('equipos/<int:pk>/', views.EquipoDetailView.as_view(), name='equipo_detail'),
    path('equipos/<int:pk>/editar/', views.EquipoUpdateView.as_view(), name='equipo_update'),
    path('equipos/<int:pk>/eliminar/', views.EquipoDeleteView.as_view(), name='equipo_delete'),
    # CRUD Ranking
    path('ranking/', views.RankingListView.as_view(), name='ranking_list'),
    path('ranking/nuevo/', views.RankingCreateView.as_view(), name='ranking_create'),
    path('ranking/<int:pk>/editar/', views.RankingUpdateView.as_view(), name='ranking_update'),
    path('ranking/<int:pk>/eliminar/', views.RankingDeleteView.as_view(), name='ranking_delete'),
    path('ranking/', views.RankingListView.as_view(), name='ranking_list'),
    # Otras rutas...
    path('posionamientoRes/',views.posisionamientosviews, name='posionamientoRes'),
    path('ranking2/',views.ranking_list, name='ranking2'),
    path('ranking3/<int:pk>/',views.ranking_detail),
    path('login/', login_view, name='login'),
    path('registro/', registro_view, name='registro'),
    path('logout/', logout_view, name='logout'),
    path('recuperar-cuenta/', views_auth.password_reset_request, name='password_reset_request'),
    path('establecer-contrasena/<str:token>/', views_auth.set_password, name='set_password'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('logout/', views_auth.logout_view, name='logout'),
    path('matriz-enfrentamientos/', views.matriz_enfrentamientos, name='matriz_enfrentamientos'),
    path('llaves-eliminacion/', views.tabla_eliminacion_directa, name='tabla_eliminacion_directa'),
    # CRUD Usuario
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/registrar/', views.registrar_usuario, name='registrar_usuario'),
    path('usuarios/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', UsuarioDeleteView.as_view(), name='usuario_confirm_delete'),
    path('api/usuarios/<int:pk>/', usuario_api_detail, name='usuario_api_detail'),
    # CRUD Institucion
    path('instituciones/', views.InstitucionListView.as_view(), name='instituciones_list'),
    path('instituciones/nuevo/', views.InstitucionCreateView.as_view(), name='instituciones_create'),
    path('instituciones/<int:pk>/editar/', views.InstitucionUpdateView.as_view(), name='instituciones_update'),
    path('instituciones/<int:pk>/eliminar/', views.InstitucionDeleteView.as_view(), name='instituciones_delete'),
    path('instituciones/<int:pk>/', views.InstitucionDetailView.as_view(), name='instituciones_detail'),
    # CRUD Asignacion
    path('asignaciones/', views.AsignacionListView.as_view(), name='asignaciones_list'),
    path('asignaciones/nuevo/', views.AsignacionCreateView.as_view(), name='asignaciones_create'),
    path('asignaciones/<int:pk>/editar/', views.AsignacionUpdateView.as_view(), name='asignaciones_update'),
    path('asignaciones/<int:pk>/eliminar/', views.AsignacionDeleteView.as_view(), name='asignaciones_delete'),
    path('asignaciones/<int:pk>/', views.AsignacionDetailView.as_view(), name='asignaciones_detail'),
    # CRUD Participante
    path('participantes/', views.ParticipanteListView.as_view(), name='participantes_list'),
    path('participantes/nuevo/', views.ParticipanteCreateView.as_view(), name='participantes_create'),
    path('participantes/<int:pk>/editar/', views.ParticipanteUpdateView.as_view(), name='participantes_update'),
    path('participantes/<int:pk>/eliminar/', views.ParticipanteDeleteView.as_view(), name='participantes_delete'),
    path('participantes/<int:pk>/', views.ParticipanteDetailView.as_view(), name='participantes_detail'),
    # CRUD Puntaje
    path('puntajes/', views.PuntajeListView.as_view(), name='puntajes_list'),
    path('puntajes/nuevo/', views.PuntajeCreateView.as_view(), name='puntajes_create'),
    path('puntajes/<int:pk>/editar/', views.PuntajeUpdateView.as_view(), name='puntajes_update'),
    path('puntajes/<int:pk>/eliminar/', views.PuntajeDeleteView.as_view(), name='puntajes_delete'),
    path('puntajes/<int:pk>/', views.PuntajeDetailView.as_view(), name='puntajes_detail'),
    # CRUD Backup
    path('backups/', views.BackupListView.as_view(), name='backups_list'),
    path('backups/nuevo/', views.BackupCreateView.as_view(), name='backups_create'),
    path('backups/<int:pk>/eliminar/', views.BackupDeleteView.as_view(), name='backups_delete'),
    path('backups/<int:pk>/', views.BackupDetailView.as_view(), name='backups_detail'),
    path('backups/<int:pk>/editar/', views.BackupUpdateView.as_view(), name='backups_update'),
    # CRUD Sala
    path('salas/', views.SalaListView.as_view(), name='sala_list'),
    path('salas/nueva/', views.SalaCreateView.as_view(), name='sala_create'),
    path('salas/<int:pk>/', views.SalaDetailView.as_view(), name='sala_detail'),
    path('salas/<int:pk>/editar/', views.SalaUpdateView.as_view(), name='sala_update'),
    path('salas/<int:pk>/eliminar/', views.SalaDeleteView.as_view(), name='sala_delete'),
    # CRUD Resultado
    path('resultados/', views.ResultadoListView.as_view(), name='resultado_list'),
    path('resultados/nuevo/', views.ResultadoCreateView.as_view(), name='resultado_create'),
    path('resultados/<int:pk>/', views.ResultadoDetailView.as_view(), name='resultado_detail'),
    path('resultados/<int:pk>/editar/', views.ResultadoUpdateView.as_view(), name='resultado_update'),
    path('resultados/<int:pk>/eliminar/', views.ResultadoDeleteView.as_view(), name='resultado_delete'),
    # CRUD Ronda
    path('rondas/', views.RondaListView.as_view(), name='ronda_list'),
    path('rondas/nueva/', views.RondaCreateView.as_view(), name='ronda_create'),
    path('rondas/<int:pk>/', views.RondaDetailView.as_view(), name='ronda_detail'),
    path('rondas/<int:pk>/editar/', views.RondaUpdateView.as_view(), name='ronda_update'),
    path('rondas/<int:pk>/eliminar/', views.RondaDeleteView.as_view(), name='ronda_delete'),

]
