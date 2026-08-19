from django.urls import path
from . import views

app_name = 'clientes'

urlpatterns = [
    # CRUD de EmpresaCliente
    path('', views.EmpresaClienteListView.as_view(), name='lista'),
    path('nova/', views.EmpresaClienteCreateView.as_view(), name='criar'),
    path('<int:pk>/', views.EmpresaClienteDetailView.as_view(), name='detalhe'),
    path('<int:pk>/editar/', views.EmpresaClienteUpdateView.as_view(), name='editar'),
    path('<int:pk>/excluir/', views.EmpresaClienteDeleteView.as_view(), name='excluir'),
     
    # CRUD de contatos
    path('contatos/<int:pk>/', views.detalhe_contato, name='detalhe_contato'),
    path('empresa/<int:empresa_pk>/contatos/novo/', views.criar_contato, name='criar_contato'),
    path('contatos/<int:pk>/editar/', views.editar_contato, name='editar_contato'),
    path('contatos/<int:pk>/excluir/', views.excluir_contato, name='excluir_contato'),
]
