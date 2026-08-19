from django.contrib import admin
from .models import EmpresaCliente, Contato

@admin.register(EmpresaCliente)
class EmpresaClienteAdmin(admin.ModelAdmin):
    list_display = ('nome_fantasia', 'razao_social', 'setor', 'porte', 'criado_em')
    list_filter = ('porte', 'setor')
    search_fields = ('razao_social', 'nome_fantasia', 'cnpj')
    
@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'empresa', 'cargo', 'email', 'decisor')
    list_filter = ('decisor',)
    search_fields = ('nome', 'email', 'empresa__razao_social', 'empresa__nome_fantasia')

