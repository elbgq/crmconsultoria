from django import forms
from .models import Oportunidade

class OportunidadeForm(forms.ModelForm):
    class Meta:
        model = Oportunidade
        fields = [
            'titulo', 'empresa_cliente', 'contato_principal', 'consultor_responsavel',
            'area', 'tipo_contrato', 'valor_estimado', 'horas_estimadas', 'valor_hora',
            'probabilidade', 'estagio', 'origem',
            'data_inicio_prevista', 'duracao_estimada_semanas', 'data_fechamento_real',
            'motivo_perda', 'observacoes',
        ]
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'empresa_cliente': forms.Select(attrs={'class': 'form-select'}),
            'contato_principal': forms.Select(attrs={'class': 'form-select'}),
            'consultor_responsavel': forms.Select(attrs={'class': 'form-select'}),
            'area': forms.Select(attrs={'class': 'form-select'}),
            'tipo_contrato': forms.Select(attrs={'class': 'form-select'}),
            'valor_estimado': forms.NumberInput(attrs={'class': 'form-control'}),
            'horas_estimadas': forms.NumberInput(attrs={'class': 'form-control'}),
            'valor_hora': forms.NumberInput(attrs={'class': 'form-control'}),
            'probabilidade': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 100}),
            'estagio': forms.Select(attrs={'class': 'form-select'}),
            'origem': forms.TextInput(attrs={'class': 'form-control'}),
            'data_inicio_prevista': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'duracao_estimada_semanas': forms.NumberInput(attrs={'class': 'form-control'}),
            'data_fechamento_real': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'motivo_perda': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
        