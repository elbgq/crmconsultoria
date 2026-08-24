from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.messages.views import SuccessMessageMixin
from .models import EmpresaCliente, Contato
from .forms import EmpresaClienteForm, ContatoForm
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse


class EmpresaClienteListView(LoginRequiredMixin, ListView):
    model = EmpresaCliente
    template_name = 'clientes/lista.html'
    context_object_name = 'empresas'
    paginate_by = 20

    def get_queryset(self):
        qs = super().get_queryset()
        busca = self.request.GET.get('busca')
        if busca:
            qs = qs.filter(razao_social__icontains=busca) | qs.filter(nome_fantasia__icontains=busca)
        return qs

# CRUD de EmpresaCliente
class EmpresaClienteDetailView(LoginRequiredMixin, DetailView):
    model = EmpresaCliente
    template_name = 'clientes/detalhe.html'
    context_object_name = 'empresa'


class EmpresaClienteCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = EmpresaCliente
    form_class = EmpresaClienteForm
    template_name = 'clientes/formulario.html'
    success_url = reverse_lazy('clientes:lista')
    success_message = "Empresa cliente criada com sucesso."


class EmpresaClienteUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = EmpresaCliente
    form_class = EmpresaClienteForm
    template_name = 'clientes/formulario.html'
    success_url = reverse_lazy('clientes:lista')
    success_message = "Empresa cliente atualizada com sucesso."


class EmpresaClienteDeleteView(LoginRequiredMixin, DeleteView):
    model = EmpresaCliente
    template_name = 'clientes/confirma_exclusao.html'
    success_url = reverse_lazy('clientes:lista')


# CRUD de Contato (pessoa) vinculada a uma empresa cliente
@login_required
def detalhe_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    contexto = {'contato': contato}
    return render(request, 'clientes/detalhe_contato.html', contexto)


@login_required
def criar_contato(request, empresa_pk=None):
    if request.method == 'POST':
        form = ContatoForm(request.POST)
        if form.is_valid():
            contato = form.save()
            messages.success(request, 'Contato cadastrado com sucesso.')
            return redirect('clientes:detalhe', pk=contato.empresa.pk)
    else:
        initial = {'empresa': empresa_pk} if empresa_pk else {}
        form = ContatoForm(initial=initial)
    return render(request, 'clientes/formulario_contato.html', {'form': form})


@login_required
def editar_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    if request.method == 'POST':
        form = ContatoForm(request.POST, instance=contato)
        if form.is_valid():
            form.save()
            messages.success(request, 'Contato atualizado.')
            return redirect('clientes:detalhe_contato', pk=contato.pk)
    else:
        form = ContatoForm(instance=contato)
    return render(request, 'clientes/formulario_contato.html', {'form': form, 'contato': contato})


@login_required
def excluir_contato(request, pk):
    contato = get_object_or_404(Contato, pk=pk)
    empresa_pk = contato.empresa.pk
    if request.method == 'POST':
        contato.delete()
        messages.success(request, 'Contato excluído.')
        return redirect('clientes:detalhe', pk=empresa_pk)
    return render(request, 'clientes/confirma_exclusao_contato.html', {'contato': contato})


@login_required
def contatos_por_empresa(request):
    empresa_id = request.GET.get('empresa_id')
    contatos = Contato.objects.filter(empresa_id=empresa_id).order_by('nome') if empresa_id else Contato.objects.none()
    data = [{'id': c.id, 'nome': str(c)} for c in contatos]
    return JsonResponse(data, safe=False)

# def contatos_por_empresa(request, empresa_id):
#    contatos = Contato.objects.filter(empresa_id=empresa_id).values('id', 'nome')
#    return JsonResponse(list(contatos), safe=False)
