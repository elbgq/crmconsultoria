from django import forms
from .models import Interacao


class InteracaoForm(forms.ModelForm):
    class Meta:
        model = Interacao
        fields = ['contato', 'oportunidade', 'tipo', 'assunto', 'descricao', 'data_interacao']
        widgets = {
            'data_interacao': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'descricao': forms.Textarea(attrs={'rows': 4}),
        }
    