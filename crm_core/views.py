from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.db.models import Sum, Count
from clientes.models import EmpresaCliente
from oportunidades.models import Oportunidade


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'crm_core/home.html'
 
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        oportunidades_abertas = Oportunidade.objects.exclude(estagio__in=['ganho', 'perdido'])

        context['total_empresas'] = EmpresaCliente.objects.count()
        context['total_oportunidades_abertas'] = oportunidades_abertas.count()
        context['valor_em_negociacao'] = oportunidades_abertas.aggregate(total=Sum('valor_estimado'))['total'] or 0
        context['por_estagio'] = (
            Oportunidade.objects.values('estagio').annotate(total=Count('id')).order_by('estagio')
        )
        context['ultimas_oportunidades'] = Oportunidade.objects.select_related('empresa_cliente').order_by('-criado_em')[:5]
        return context
    