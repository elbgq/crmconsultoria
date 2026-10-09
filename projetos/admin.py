from django.contrib import admin
from .models import ProjetoConsultoria, Entrega, LancamentoHoras


class EntregaInline(admin.TabularInline):
    model = Entrega
    extra = 1


class LancamentoHorasInline(admin.TabularInline):
    model = LancamentoHoras
    extra = 0


@admin.register(ProjetoConsultoria)
class ProjetoConsultoriaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'status', 'gerente_projeto', 'percentual_horas_consumidas')
    list_filter = ('status',)
    readonly_fields = ('horas_consumidas',)
    inlines = [EntregaInline, LancamentoHorasInline]


admin.site.register(Entrega)
admin.site.register(LancamentoHoras)
