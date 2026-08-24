from django import forms
from .models import ProjetoConsultoria, Entrega


class ProjetoConsultoriaForm(forms.ModelForm):
    class Meta:
        model = ProjetoConsultoria
        fields = [
            'nome', 'status', 'equipe', 'gerente_projeto',
            'data_inicio_real', 'data_fim_prevista', 'data_fim_real',
            'horas_estimadas', 'horas_consumidas', 'observacoes',
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
