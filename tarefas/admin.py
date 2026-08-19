from django.contrib import admin
from .models import Tarefa


@admin.register(Tarefa)
class TarefaAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'responsavel', 'prioridade', 'data_vencimento', 'concluida')
    list_filter = ('concluida', 'prioridade', 'tipo')
    search_fields = ('titulo',)
