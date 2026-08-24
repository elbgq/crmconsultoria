from django import forms
from .models import Oportunidade
from clientes.models import Contato

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
            #'motivo_perda': forms.TextInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        empresa = kwargs.pop('empresa', None)
        super().__init__(*args, **kwargs)
        
        # Edição
        if self.instance and self.instance.pk:
            empresa = self.instance.empresa_cliente

        # Criação via POST
        if not empresa:
            empresa_id = self.data.get('empresa_cliente')
            if empresa_id:
                from clientes.models import EmpresaCliente
                try:
                    empresa = EmpresaCliente.objects.get(pk=empresa_id)
                except EmpresaCliente.DoesNotExist:
                    empresa = None

        # Filtra contatos
        if empresa:
            self.fields['contato_principal'].queryset = Contato.objects.filter(empresa=empresa) # type: ignore
        else:
            self.fields['contato_principal'].queryset = Contato.objects.none() # type: ignore

    # Validação para garantir que motivo_perda seja preenchido se a oportunidade for "perdida"
    def clean(self):
        cleaned = super().clean()
        estagio = cleaned.get('estagio')
        motivo = cleaned.get('motivo_perda')

        if estagio == 'perdido' and not motivo:
            self.add_error('motivo_perda', 'Informe o motivo da perda.')

        return cleaned