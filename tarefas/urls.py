# tarefas/urls.py
from django.urls import path
from . import views

app_name = 'tarefas'

urlpatterns = [
    path('', views.TarefaListaView.as_view(), name='tarefas_lista'),
    path('nova/', views.TarefaCreateView.as_view(), name='tarefa_nova'),
    path('<int:pk>/editar/', views.TarefaUpdateView.as_view(), name='tarefa_editar'),
    path('<int:pk>/concluir/', views.tarefa_concluir, name='tarefa_concluir'),
]
