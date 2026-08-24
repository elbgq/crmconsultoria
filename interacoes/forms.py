from django import forms
from .models import Interacao
from clientes.models import Contato


class InteracaoForm(forms.ModelForm):
    class Meta:
        model = Interacao
        fields = ['contato', 'oportunidade', 'tipo', 'assunto', 'descricao', 'data_interacao']
        widgets = {
            'data_interacao': forms.TextInput(attrs={
                'class': 'form-control datepicker',
                'autocomplete': 'off'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)

        # Se a interação veio de uma oportunidade, filtrar contatos pela empresa
        if empresa:
            self.fields['contato'].queryset = Contato.objects.filter(empresa=empresa) # type: ignore
        
        if self.instance and self.instance.data_interacao:
            self.fields['data_interacao'].initial = self.instance.data_interacao.strftime("%d/%m/%Y %H:%M")  
    