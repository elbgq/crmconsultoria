from django.contrib import admin
from .models import Oportunidade, HistoricoEstagio

@admin.register(Oportunidade)
class OportunidadeAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'empresa_cliente', 'valor_estimado', 'estagio', 'data_fechamento_real')
    list_filter = ('estagio', 'area', 'tipo_contrato')
    search_fields = ('titulo', 'empresa_cliente__razao_social', 'empresa_cliente__nome_fantasia')
    
@admin.register(HistoricoEstagio)
class HistoricoEstagioAdmin(admin.ModelAdmin):
    list_display = ('oportunidade', 'estagio_anterior', 'estagio_novo', 'data_mudanca', 'alterado_por')
    list_filter = ('estagio_novo',)
    search_fields = ('oportunidade__titulo',)
