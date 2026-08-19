# relatorios/services.py
from django.db.models import Sum, Count, Avg, Q
from oportunidades.models import Oportunidade


# Separar as queries agregadas num arquivo services.py
# (em vez de deixar tudo dentro de views.py) facilita:
#
# Reutilizar essas mesmas consultas depois numa API REST, se você decidir expor dados via DRF
# Testar as regras de negócio isoladamente, sem precisar simular uma requisição HTTP
# Manter a view limpa, só orquestrando o que mostrar

# Funil de vendas — quantidade e valor por estágio
def funil_de_vendas():
    return (
        Oportunidade.objects
        .values('estagio')
        .annotate(
            quantidade=Count('id'),
            valor_total=Sum('valor_estimado'),
        )
        .order_by('estagio')
    )

# Taxa de conversão por consultor
def conversao_por_consultor():
    return (
        Oportunidade.objects
        .values('consultor_responsavel__username', 'consultor_responsavel__first_name')
        .annotate(
            total=Count('id'),
            ganhas=Count('id', filter=Q(estagio='ganho')),
            perdidas=Count('id', filter=Q(estagio='perdido')),
        )
    )


# Receita por tipo de contrato e área de consultoria
def receita_por_tipo_contrato():
    return (
        Oportunidade.objects
        .filter(estagio='ganho')
        .values('tipo_contrato')
        .annotate(receita_total=Sum('valor_estimado'), quantidade=Count('id'))
    )


def receita_por_area():
    return (
        Oportunidade.objects
        .filter(estagio='ganho')
        .values('area')
        .annotate(receita_total=Sum('valor_estimado'), quantidade=Count('id'))
    )

# Margem por projeto (horas estimadas vs. consumidas)
# Esse é o mais importante do ponto de vista financeiro de uma consultoria
from projetos.models import ProjetoConsultoria

def margem_projetos():
    projetos = ProjetoConsultoria.objects.filter(horas_estimadas__isnull=False)
    resultado = []
    for p in projetos:
        percentual = p.percentual_horas_consumidas
        resultado.append({
            'projeto': p.nome,
            'horas_estimadas': p.horas_estimadas,
            'horas_consumidas': p.horas_consumidas,
            'percentual_consumido': percentual,
            'status_margem': 'Alerta' if percentual and percentual > 90 else 'OK',
        })
    return resultado

# Tarefas atrasadas por responsável
from django.utils import timezone
from tarefas.models import Tarefa

def tarefas_atrasadas_por_responsavel():
    return (
        Tarefa.objects
        .filter(concluida=False, data_vencimento__lt=timezone.now())
        .values('responsavel__username')
        .annotate(quantidade=Count('id'))
        .order_by('-quantidade')
    )

