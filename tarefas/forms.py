from django import forms
from .models import Tarefa
 
class TarefaForm(forms.ModelForm):
    class Meta:
        model = Tarefa
        fields = [
            'titulo',
            'descricao',
            'tipo',
            'prioridade',
            'data_vencimento',
            'oportunidade',
            'projeto',
        ]
        widgets = {
            'data_vencimento': forms.TextInput(attrs={
                'class': 'form-control datetimepicker',
                'autocomplete': 'off',
            }),
        }
