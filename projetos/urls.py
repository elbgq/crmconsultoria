from django.urls import path
from . import views

app_name = 'projetos'

urlpatterns = [
    path('', views.lista_projetos, name='lista'),
    path('<int:pk>/', views.detalhe_projeto, name='detalhe'),
    path('<int:pk>/editar/', views.editar_projeto, name='editar_projeto'),
    path('<int:pk>/excluir/', views.excluir_projeto, name='excluir_projeto'),
    path('<int:projeto_pk>/entregas/adicionar/', views.adicionar_entrega, name='adicionar_entrega'),
    path('<int:projeto_pk>/entregas/<int:entrega_pk>/editar/', views.editar_entrega, name='editar_entrega'),
]
