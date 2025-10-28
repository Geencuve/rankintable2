from django.urls import path
from . import views

urlpatterns = [
    path('', views.tabla_posicionamiento, name='home'),
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
]
