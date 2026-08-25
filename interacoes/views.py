# Como interações normalmente são visualizadas dentro do contexto de um contato
# ou oportunidade (não como lista solta), montamos as views assim.

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.utils import timezone

from .models import Interacao, Oportunidade
from .forms import InteracaoForm
from clientes.models import Contato

# Interações são normalmente registradas dentro do contexto de um contato.
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
            # Redirecionamento seguro
            if interacao.oportunidade:
                return redirect('oportunidades:detalhe', pk=interacao.oportunidade.pk)
            return redirect('clientes:detalhe_contato', pk=contato.pk)
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
            # Redirecionamento seguro
            if interacao.oportunidade:
                return redirect('oportunidades:detalhe', pk=interacao.oportunidade.pk)
            return redirect('clientes:detalhe_contato', pk=interacao.contato.pk)
    else:
        form = InteracaoForm(instance=interacao)
    
    return render(request, 'interacoes/form.html', {'form': form, 'contato': interacao.contato})


@login_required
def excluir_interacao(request, pk):
    interacao = get_object_or_404(Interacao, pk=pk)
    #contato_pk = interacao.contato.pk
    if request.method == 'POST':
        oportunidade = interacao.oportunidade
        contato = interacao.contato
        interacao.delete()
        messages.success(request, 'Interação excluída.')
        # Redirecionamento seguro
        if oportunidade:
            return redirect('oportunidades:detalhe', pk=oportunidade.pk)
        return redirect('clientes:detalhe_contato', pk=contato.pk)
    return render(request, 'interacoes/confirmar_exclusao.html', {'interacao': interacao})

# Interações também podem ser registradas dentro do contexto de uma oportunidade, caso seja necessário.
@login_required
def registrar_interacao_oportunidade(request, oportunidade_pk):
    oportunidade = get_object_or_404(Oportunidade, pk=oportunidade_pk)
    empresa = oportunidade.empresa_cliente  # ← aqui está a empresa

    if request.method == 'POST':
        form = InteracaoForm(request.POST)
        if form.is_valid():
            interacao = form.save(commit=False)
            interacao.oportunidade = oportunidade
            interacao.responsavel = request.user
            interacao.save()
            messages.success(request, 'Interação registrada com sucesso.')
            return redirect('oportunidades:detalhe', pk=oportunidade.pk)
    else:
        form = InteracaoForm(
            initial={'data_interacao': timezone.now()},
            empresa=empresa
        )

    return render(request, 'interacoes/form.html', {
        'form': form,
        'oportunidade': oportunidade
    })
