from django.urls import path
from . import views

app_name = 'interacoes'

urlpatterns = [
    path('contato/<int:contato_pk>/registrar/', views.registrar_interacao, name='registrar'),
    path('<int:pk>/editar/', views.editar_interacao, name='editar'),
    path('<int:pk>/excluir/', views.excluir_interacao, name='excluir'),
]
