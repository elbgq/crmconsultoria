# relatorios/views.py
import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from . import services
 

@login_required
def dashboard(request):
    funil = list(services.funil_de_vendas())
    conversao = list(services.conversao_por_consultor())
    receita_contrato = list(services.receita_por_tipo_contrato())
    receita_area = list(services.receita_por_area())
    margem_projetos = services.margem_projetos()
    tarefas_atrasadas = list(services.tarefas_atrasadas_por_responsavel())

    contexto = {
        'funil': funil,
        'conversao': conversao,
        'receita_contrato': receita_contrato,
        'receita_area': receita_area,
        'margem_projetos': margem_projetos,
        'tarefas_atrasadas': tarefas_atrasadas,
        # Versões em JSON para os gráficos JS
        'funil_json': json.dumps(funil, default=str),
        'receita_area_json': json.dumps(receita_area, default=str),
        'receita_contrato_json': json.dumps(receita_contrato, default=str),
    }
    return render(request, 'relatorios/dashboard.html', contexto)
