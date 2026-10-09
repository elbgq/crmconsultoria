from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Sum
from .models import ProjetoConsultoria, Entrega, LancamentoHoras
from .forms import ProjetoConsultoriaForm, EntregaForm, LancamentoHorasForm
from usuarios.permissions import eh_consultor_senior_ou_socio
from django.utils import timezone


# Observação: não incluí criar_projeto como view separada porque, lembra do signal que fizemos?
# O projeto é criado automaticamente quando a oportunidade vira "Ganho". Faz sentido manter assim
# — evita duplicidade e garante que todo projeto tenha uma oportunidade de origem.

@login_required
def lista_projetos(request):
    status_filtro = request.GET.get('status', '')
    projetos = ProjetoConsultoria.objects.select_related('gerente_projeto', 'oportunidade_origem__empresa_cliente')

    if status_filtro:
        projetos = projetos.filter(status=status_filtro)

    contexto = {
        'projetos': projetos,
        'status_filtro': status_filtro,
        'status_choices': ProjetoConsultoria._meta.get_field('status').choices,
    }
    return render(request, 'projetos/lista.html', contexto)


@login_required
def detalhe_projeto(request, pk):
    projeto = get_object_or_404(ProjetoConsultoria, pk=pk)
    entregas = projeto.entregas.annotate(total_horas=Sum('lancamentos__horas')) # type: ignore
    lancamentos = list(projeto.lancamentos.select_related('usuario', 'entrega'))  # type: ignore
    for l in lancamentos:
        l.pode_gerir = _pode_gerir_lancamento(request.user, l)
    horas_por_consultor = (
        projeto.lancamentos.values('usuario__first_name', 'usuario__username')  # type: ignore
        .annotate(total=Sum('horas')).order_by('-total')
    )
    contexto = {
        'projeto': projeto, 'entregas': entregas,
        'lancamentos': lancamentos, 'horas_por_consultor': horas_por_consultor,
    }
    return render(request, 'projetos/detalhe.html', contexto)


@login_required
def editar_projeto(request, pk):
    projeto = get_object_or_404(ProjetoConsultoria, pk=pk)
    if request.method == 'POST':
        form = ProjetoConsultoriaForm(request.POST, instance=projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Projeto atualizado com sucesso.')
            return redirect('projetos:detalhe', pk=projeto.pk)
    else:
        form = ProjetoConsultoriaForm(instance=projeto)
    return render(request, 'projetos/form.html', {'form': form, 'projeto': projeto})


@login_required
def excluir_projeto(request, pk):
    projeto = get_object_or_404(ProjetoConsultoria, pk=pk)
    if request.method == 'POST':
        projeto.delete()
        messages.success(request, 'Projeto excluído.')
        return redirect('projetos:lista')
    return render(request, 'projetos/confirmar_exclusao.html', {'projeto': projeto})


# --- Entregas (dentro do contexto de um projeto) ---

@login_required
def adicionar_entrega(request, projeto_pk):
    projeto = get_object_or_404(ProjetoConsultoria, pk=projeto_pk)
    if request.method == 'POST':
        form = EntregaForm(request.POST)
        if form.is_valid():
            entrega = form.save(commit=False)
            entrega.projeto = projeto
            entrega.save()
            messages.success(request, 'Entrega adicionada.')
            return redirect('projetos:detalhe', pk=projeto.pk)
    else:
        form = EntregaForm()
    return render(request, 'projetos/entrega_form.html', {'form': form, 'projeto': projeto})


@login_required
def editar_entrega(request, projeto_pk, entrega_pk):
    entrega = get_object_or_404(Entrega, pk=entrega_pk, projeto_id=projeto_pk)
    if request.method == 'POST':
        form = EntregaForm(request.POST, instance=entrega)
        if form.is_valid():
            form.save()
            messages.success(request, 'Entrega atualizada.')
            return redirect('projetos:detalhe', pk=entrega.projeto.pk)
    else:
        form = EntregaForm(instance=entrega)
    return render(request, 'projetos/entrega_form.html', {'form': form, 'projeto': entrega.projeto})
 
# Para o botão de concluir uma entrega/fase.
def concluir_entrega(request, entrega_id):
    entrega = get_object_or_404(Entrega, id=entrega_id)
    entrega.concluida = True
    entrega.data_entregue = timezone.now().date()
    entrega.save()
    return redirect('projetos:detalhe', pk=entrega.projeto.id) # type: ignore


# --- Lançamento de horas ---

def _pode_gerir_lancamento(user, lancamento):
    """Cada consultor edita/exclui os próprios lançamentos; superusuário, sócio e sênior, todos."""
    return (
        user.is_superuser
        or eh_consultor_senior_ou_socio(user)
        or lancamento.usuario_id == user.pk
    )


@login_required
def lancar_horas(request, projeto_pk):
    projeto = get_object_or_404(ProjetoConsultoria, pk=projeto_pk)
    if request.method == 'POST':
        form = LancamentoHorasForm(request.POST, projeto=projeto)
        if form.is_valid():
            lancamento = form.save(commit=False)
            lancamento.projeto = projeto
            lancamento.usuario = request.user
            lancamento.save()
            messages.success(request, 'Horas lançadas.')
            return redirect('projetos:detalhe', pk=projeto.pk)
    else:
        form = LancamentoHorasForm(projeto=projeto)
    return render(request, 'projetos/horas_form.html', {'form': form, 'projeto': projeto})


@login_required
def editar_horas(request, pk):
    lancamento = get_object_or_404(LancamentoHoras, pk=pk)
    if not _pode_gerir_lancamento(request.user, lancamento):
        raise PermissionDenied
    if request.method == 'POST':
        form = LancamentoHorasForm(request.POST, instance=lancamento, projeto=lancamento.projeto)
        if form.is_valid():
            form.save()
            messages.success(request, 'Lançamento atualizado.')
            return redirect('projetos:detalhe', pk=lancamento.projeto_id) # type: ignore
    else:
        form = LancamentoHorasForm(instance=lancamento, projeto=lancamento.projeto)
    return render(request, 'projetos/horas_form.html', {'form': form, 'projeto': lancamento.projeto})


@login_required
def excluir_horas(request, pk):
    lancamento = get_object_or_404(LancamentoHoras, pk=pk)
    if not _pode_gerir_lancamento(request.user, lancamento):
        raise PermissionDenied
    projeto_pk = lancamento.projeto_id # type: ignore
    if request.method == 'POST':
        lancamento.delete()
        messages.success(request, 'Lançamento excluído.')
        return redirect('projetos:detalhe', pk=projeto_pk)
    return render(request, 'projetos/horas_confirmar_exclusao.html', {'lancamento': lancamento})
