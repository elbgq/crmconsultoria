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
            'data_prevista': forms.DateInput(attrs={'type': 'date'}),
            'data_entregue': forms.DateInput(attrs={'type': 'date'}),
            'descricao': forms.Textarea(attrs={'rows': 2}),
        }
        