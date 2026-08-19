# Como interações normalmente são visualizadas dentro do contexto de um contato
# ou oportunidade (não como lista solta), montamos as views assim.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone

from .models import Interacao
from .forms import InteracaoForm
from clientes.models import Contato


@login_required
def registrar_interacao(request, contato_pk):
    contato = get_object_or_404(Contato, pk=contato_pk)

    if request.method == 'POST':
        form = InteracaoForm(request.POST)
        if form.is_valid():
            interacao = form.save(commit=False)
            interacao.contato = contato
            interacao.responsavel = request.user
            interacao.save()
            messages.success(request, 'Interação registrada com sucesso.')
            return redirect('clientes:detalhe', pk=contato.pk)
    else:
        form = InteracaoForm(initial={'contato': contato, 'data_interacao': timezone.now()})
        form.fields['contato'].widget = form.fields['contato'].hidden_widget()

    return render(request, 'interacoes/form.html', {'form': form, 'contato': contato})


@login_required
def editar_interacao(request, pk):
    interacao = get_object_or_404(Interacao, pk=pk)

    if request.method == 'POST':
        form = InteracaoForm(request.POST, instance=interacao)
        if form.is_valid():
            form.save()
            messages.success(request, 'Interação atualizada.')
            return redirect('clientes:detalhe', pk=interacao.contato.pk)
    else:
        form = InteracaoForm(instance=interacao)

    return render(request, 'interacoes/form.html', {'form': form, 'contato': interacao.contato})


@login_required
def excluir_interacao(request, pk):
    interacao = get_object_or_404(Interacao, pk=pk)
    contato_pk = interacao.contato.pk
    if request.method == 'POST':
        interacao.delete()
        messages.success(request, 'Interação excluída.')
        return redirect('clientes:detalhe', pk=contato_pk)
    return render(request, 'interacoes/confirmar_exclusao.html', {'interacao': interacao})
