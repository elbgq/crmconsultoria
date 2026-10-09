from django import forms
from django.utils import timezone

from .models import ProjetoConsultoria, Entrega, LancamentoHoras


class ProjetoConsultoriaForm(forms.ModelForm):
    class Meta:
        model = ProjetoConsultoria
        fields = [
            'nome', 'status', 'equipe', 'gerente_projeto',
            'data_inicio_real', 'data_fim_prevista', 'data_fim_real',
            'horas_estimadas', 'observacoes',
        ]
        widgets = {
            'data_inicio_real': forms.DateInput(attrs={'type': 'date'}),
            'data_fim_prevista': forms.DateInput(attrs={'type': 'date'}),
            'data_fim_real': forms.DateInput(attrs={'type': 'date'}),
            'observacoes': forms.Textarea(attrs={'rows': 3}),
            'equipe': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }

 
class EntregaForm(forms.ModelForm):
    class Meta:
        model = Entrega
        fields = ['nome', 'descricao', 'data_prevista', 'data_entregue', 'responsavel', 'concluida']
        widgets = {
            # Especifique o formato de data para os campos de data e preserva o seu valor na edição.
            'data_prevista': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'data_entregue': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['data_prevista'].input_formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M'] # type: ignore
        self.fields['data_entregue'].input_formats = ['%Y-%m-%d', '%Y-%m-%dT%H:%M'] # type: ignore


class LancamentoHorasForm(forms.ModelForm):
    class Meta:
        model = LancamentoHoras
        fields = ['data', 'horas', 'entrega', 'descricao']
        widgets = {
            'data': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'horas': forms.NumberInput(attrs={'step': '0.25', 'min': '0.25', 'max': '24'}),
        }

    def __init__(self, *args, projeto=None, **kwargs):
        super().__init__(*args, **kwargs)
        # A fase é opcional e só pode ser uma entrega do próprio projeto
        self.fields['entrega'].queryset = (  # type: ignore
            projeto.entregas.all() if projeto else Entrega.objects.none()
        )
        self.fields['entrega'].empty_label = 'Projeto como um todo (sem fase)'  # type: ignore
        self.fields['data'].input_formats = ['%Y-%m-%d', '%d/%m/%Y']  # type: ignore
        self.fields['data'].widget.attrs['max'] = timezone.localdate().isoformat()
