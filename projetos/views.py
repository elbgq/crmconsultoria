from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ProjetoConsultoria, Entrega
from .forms import ProjetoConsultoriaForm, EntregaForm

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
    entregas = projeto.entregas.all()
    contexto = {'projeto': projeto, 'entregas': entregas}
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
