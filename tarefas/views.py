from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Tarefa
from .forms import TarefaForm

class TarefaListaView(LoginRequiredMixin, ListView):
    model = Tarefa
    template_name = 'tarefas/lista.html'

    def get_queryset(self):
        return Tarefa.objects.filter(responsavel=self.request.user).order_by('data_vencimento')

class TarefaCreateView(LoginRequiredMixin, CreateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefas/form.html'

    def get_initial(self):
        initial = super().get_initial()

        oportunidade_id = self.request.GET.get('oportunidade')
        projeto_id = self.request.GET.get('projeto')

        if oportunidade_id:
            initial['oportunidade'] = oportunidade_id

        if projeto_id:
            initial['projeto'] = projeto_id

        return initial

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        oportunidade_id = self.request.GET.get('oportunidade')
        projeto_id = self.request.GET.get('projeto')

        # Se veio da oportunidade → esconder campo
        if oportunidade_id:
            form.fields['oportunidade'].widget = form.fields['oportunidade'].hidden_widget()
            form.fields['projeto'].widget = form.fields['projeto'].hidden_widget()

        # Se veio do projeto → esconder campo
        if projeto_id:
            form.fields['projeto'].widget = form.fields['projeto'].hidden_widget()
            form.fields['oportunidade'].widget = form.fields['oportunidade'].hidden_widget()

        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        from oportunidades.models import Oportunidade
        from projetos.models import ProjetoConsultoria

        oportunidade_id = self.request.GET.get('oportunidade')
        projeto_id = self.request.GET.get('projeto')

        if oportunidade_id:
            context['oportunidade'] = Oportunidade.objects.get(pk=oportunidade_id)
        if projeto_id:
            context['projeto'] = ProjetoConsultoria.objects.get(pk=projeto_id)

        return context
    
    def form_valid(self, form):
        form.instance.responsavel = self.request.user
        return super().form_valid(form)
    

class TarefaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefas/form.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarefa = self.object # type: ignore
        if tarefa.oportunidade:
            context['oportunidade'] = tarefa.oportunidade
        if tarefa.projeto:
            context['projeto'] = tarefa.projeto
        return context

def tarefa_concluir(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    tarefa.concluida = True
    tarefa.save()
    return redirect('tarefas_lista')
