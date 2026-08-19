from django.urls import path
from . import views

app_name = 'oportunidades'

urlpatterns = [
    path('', views.OportunidadeListView.as_view(), name='lista'),
    path('kanban/', views.OportunidadeKanbanView.as_view(), name='kanban'),
    path('kanban/atualizar-estagio/', views.AtualizarEstagioAjaxView.as_view(), name='atualizar_estagio_ajax'),
    path('nova/', views.OportunidadeCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.OportunidadeDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.OportunidadeUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.OportunidadeDeleteView.as_view(), name='excluir'),
    path('<int:pk>/mudar-estagio/', views.AtualizarEstagioView.as_view(), name='mudar_estagio'),
]
