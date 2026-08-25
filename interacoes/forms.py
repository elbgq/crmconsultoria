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

        # Sempre ocultar o campo oportunidade (nunca deve ser editável)
        self.fields['oportunidade'].widget = self.fields['oportunidade'].hidden_widget()
        
        # Formatar data
        if self.instance and self.instance.data_interacao:
            self.fields['data_interacao'].initial = self.instance.data_interacao.strftime("%d/%m/%Y %H:%M")
        
        # FLUXO VIA OPORTUNIDADE (criação ou edição)
        if empresa:
            self.fields['contato'].queryset = Contato.objects.filter(empresa=empresa) # type: ignore
            return
        
        # FLUXO VIA CONTATO (criação ou edição)
        # Se não veio empresa → é fluxo via contato
        self.fields['contato'].widget = self.fields['contato'].hidden_widget()
