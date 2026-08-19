from django.contrib import admin
from .models import Interacao


@admin.register(Interacao)
class InteracaoAdmin(admin.ModelAdmin):
    list_display = ('contato', 'tipo', 'assunto', 'data_interacao', 'responsavel')
    list_filter = ('tipo', 'data_interacao')
    search_fields = ('assunto', 'contato__nome')
    date_hierarchy = 'data_interacao'
    