from django.urls import path
from . import views
from .views_auth import login_view, registro_view, logout_view
from . import views_auth
from .views import UsuarioUpdateView, UsuarioDeleteView, UsuarioListView, UsuarioCreateView,usuario_api_detail



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
 # Otras rutas...
    path('ranking/', views.RankingListView.as_view(), name='ranking_list'),
    path('ranking/nuevo/', views.RankingCreateView.as_view(), name='ranking_create'),
    path('ranking/<int:pk>/editar/', views.RankingUpdateView.as_view(), name='ranking_update'),
    path('ranking/<int:pk>/eliminar/', views.RankingDeleteView.as_view(), name='ranking_delete'),
    path('ranking/', views.RankingListView.as_view(), name='ranking_list'),
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
    path('usuarios/', views.usuarios_list, name='usuarios_list'),
    path('usuarios/registrar/', views.registrar_usuario, name='registrar_usuario'),
    
    path('usuarios/', UsuarioListView.as_view(), name='usuario_list'),
    path('usuarios/nuevo/', UsuarioCreateView.as_view(), name='registrar_usuario'),
    path('usuarios/<int:pk>/editar/', UsuarioUpdateView.as_view(), name='editar_usuario'),
    path('usuarios/<int:pk>/eliminar/', UsuarioDeleteView.as_view(), name='usuario_confirm_delete'),
    path('api/usuarios/<int:pk>/', usuario_api_detail, name='usuario_api_detail'),

]
