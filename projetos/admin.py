from django.contrib import admin
from .models import ProjetoConsultoria, Entrega


class EntregaInline(admin.TabularInline):
    model = Entrega
    extra = 1


@admin.register(ProjetoConsultoria)
class ProjetoConsultoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'gerente_projeto', 'percentual_horas_consumidas')
    list_filter = ('status',)
    inlines = [EntregaInline]


admin.site.register(Entrega)
