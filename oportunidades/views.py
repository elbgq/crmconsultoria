from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Oportunidade, HistoricoEstagio
from .forms import OportunidadeForm
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views import View
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from crm_core.models import EstagioFunil


class OportunidadeListView(LoginRequiredMixin, ListView):
    model = Oportunidade
    template_name = 'oportunidades/lista.html'
    context_object_name = 'oportunidades'
    paginate_by = 10

    def get_queryset(self):
        qs = super().get_queryset().select_related('empresa_cliente')
        estagio = self.request.GET.get('estagio')
        if estagio:
            qs = qs.filter(estagio=estagio)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['estagios'] = Oportunidade._meta.get_field('estagio').choices
        context['estagio_selecionado'] = self.request.GET.get('estagio', '')
        return context


class OportunidadeDetailView(LoginRequiredMixin,DetailView):
    model = Oportunidade
    template_name = 'oportunidades/detalhe.html'
    context_object_name = 'oportunidade'


class OportunidadeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = Oportunidade
    form_class = OportunidadeForm
    template_name = 'oportunidades/formulario.html'
    success_url = reverse_lazy('oportunidades:lista')
    success_message = "Oportunidade criada com sucesso."

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        empresa_id = self.request.GET.get('empresa_cliente') or self.request.POST.get('empresa_cliente')
        
        if empresa_id:
            from clientes.models import EmpresaCliente
            try:
                kwargs['empresa'] = EmpresaCliente.objects.get(pk=empresa_id)
            except EmpresaCliente.DoesNotExist:
                kwargs['empresa'] = None
        return kwargs

class OportunidadeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Oportunidade
    form_class = OportunidadeForm
    template_name = 'oportunidades/formulario.html'
    success_url = reverse_lazy('oportunidades:lista')
    success_message = "Oportunidade atualizada com sucesso."

    def get_form_kwargs(self):
            kwargs = super().get_form_kwargs() # type: ignore
            kwargs['empresa'] = self.object.empresa_cliente # type: ignore
            return kwargs
        
class OportunidadeDeleteView(LoginRequiredMixin, DeleteView):
    model = Oportunidade
    template_name = 'oportunidades/confirma_exclusao.html'
    success_url = reverse_lazy('oportunidades:lista')

# Visão Kanban
class OportunidadeKanbanView(LoginRequiredMixin, TemplateView):
    template_name = 'oportunidades/kanban.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        oportunidades = Oportunidade.objects.select_related('empresa_cliente').all()

        colunas = []
        for valor, rotulo in EstagioFunil.choices:
            colunas.append({
                'valor': valor,
                'rotulo': rotulo,
                'oportunidades': [op for op in oportunidades if op.estagio == valor],
            })
        context['colunas'] = colunas
        return context


class AtualizarEstagioView(LoginRequiredMixin, View):
    def post(self, request, pk):
        oportunidade = get_object_or_404(Oportunidade, pk=pk)
        data = json.loads(request.body)
        novo_estagio = data.get('estagio')

        if novo_estagio not in EstagioFunil.values:
            return JsonResponse({'erro': 'Estágio inválido'}, status=400)

        estagio_anterior = oportunidade.estagio
        if estagio_anterior != novo_estagio:
            oportunidade.estagio = novo_estagio
            oportunidade.save(update_fields=['estagio'])

            HistoricoEstagio.objects.create(
                oportunidade=oportunidade,
                estagio_anterior=estagio_anterior,
                estagio_novo=novo_estagio,
                alterado_por=request.user if request.user.is_authenticated else None,
            )

        return JsonResponse({'ok': True})

# Adicionar a view de atualização (mantendo o padrão CBV, se preferir)
class AtualizarEstagioAjaxView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        try:
            dados = json.loads(request.body)
            oportunidade_id = dados.get('oportunidade_id')
            novo_estagio = dados.get('novo_estagio')
        except (json.JSONDecodeError, AttributeError):
            return JsonResponse({'erro': 'Dados inválidos'}, status=400)

        estagios_validos = [valor for valor, _ in EstagioFunil.choices]
        if novo_estagio not in estagios_validos:
            return JsonResponse({'erro': 'Estágio inválido'}, status=400)

        oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_id)
        oportunidade.estagio = novo_estagio
        oportunidade.save()  # signal de HistoricoEstagio dispara aqui

        return JsonResponse({'sucesso': True, 'novo_estagio': novo_estagio})
    

# Montagem do Kanban de oportunidades completo: view que agrupa por estágio,
# template com colunas, e o drag-and-drop funcional usando SortableJS + AJAX.
# oportunidades/views.py (adicionar a estas views existentes)

@login_required
def kanban_oportunidades(request):
    colunas = []
    for valor, label in EstagioFunil.choices:
        if valor in ('ganho', 'perdido'):
            continue  # opcional: manter fora do board ativo, ou incluir se preferir
        oportunidades = (
            Oportunidade.objects
            .filter(estagio=valor)
            .select_related('empresa_cliente', 'consultor_responsavel')
        )
        colunas.append({
            'valor': valor,
            'label': label,
            'oportunidades': oportunidades,
            'total_valor': sum(o.valor_estimado for o in oportunidades),
        })

    contexto = {'colunas': colunas}
    return render(request, 'oportunidades/kanban.html', contexto)


@require_POST
@login_required
def atualizar_estagio_ajax(request):
    try:
        dados = json.loads(request.body)
        oportunidade_id = dados.get('oportunidade_id')
        novo_estagio = dados.get('novo_estagio')
    except (json.JSONDecodeError, AttributeError):
        return JsonResponse({'erro': 'Dados inválidos'}, status=400)

    estagios_validos = [valor for valor, _ in EstagioFunil.choices]
    if novo_estagio not in estagios_validos:
        return JsonResponse({'erro': 'Estágio inválido'}, status=400)

    oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_id)
    estagio_anterior = oportunidade.estagio

    if estagio_anterior != novo_estagio:
        oportunidade.estagio = novo_estagio
        oportunidade.save()

        # CRIA O HISTÓRICO - avanço ou regresso de estágio
        HistoricoEstagio.objects.create(
            oportunidade=oportunidade,
            estagio_anterior=estagio_anterior,
            estagio_novo=novo_estagio,
            alterado_por=request.user
        )

    return JsonResponse({'sucesso': True, 'novo_estagio': novo_estagio})
