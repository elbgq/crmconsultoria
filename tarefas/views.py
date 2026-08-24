from django.views.generic import ListView, CreateView, UpdateView
from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Tarefa, Oportunidade, ProjetoConsultoria
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

        # Se veio da oportunidade → esconder ambos os campos
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
            oportunidade_id = self.request.GET.get('oportunidade')
            projeto_id = self.request.GET.get('projeto')

            # Vincula corretamente ANTES de salvar
            if oportunidade_id:
                form.instance.oportunidade = Oportunidade.objects.get(pk=oportunidade_id)
    
            if projeto_id:
                form.instance.projeto = ProjetoConsultoria.objects.get(pk=projeto_id)
    
            return super().form_valid(form)


class TarefaUpdateView(LoginRequiredMixin, UpdateView):
    model = Tarefa
    form_class = TarefaForm
    template_name = 'tarefas/form.html'
    
    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        tarefa = self.get_object()  # type: ignore

        # Se a tarefa já está vinculada a uma oportunidade → ocultar campos
        if tarefa.oportunidade: # type: ignore
            form.fields['oportunidade'].widget = form.fields['oportunidade'].hidden_widget()
            form.fields['projeto'].widget = form.fields['projeto'].hidden_widget()

        # Se a tarefa está vinculada a um projeto → ocultar campos
        if tarefa.projeto: # type: ignore
            form.fields['projeto'].widget = form.fields['projeto'].hidden_widget()
            form.fields['oportunidade'].widget = form.fields['oportunidade'].hidden_widget()

        return form
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tarefa = self.get_object()  # type: ignore
        
        if tarefa.oportunidade: # type: ignore
            context['oportunidade'] = tarefa.oportunidade # type: ignore
            
        if tarefa.projeto: # type: ignore
            context['projeto'] = tarefa.projeto # type: ignore
            
        return context
    
def tarefa_concluir(request, pk):
    tarefa = get_object_or_404(Tarefa, pk=pk)
    tarefa.concluida = True
    tarefa.save()
    
    if tarefa.oportunidade:
        return redirect('oportunidades:detalhe', pk=tarefa.oportunidade.pk)
    else:
        return redirect('tarefas:lista')

