from django import forms
from .models import EmpresaCliente, Contato

class EmpresaClienteForm(forms.ModelForm):
    class Meta:
        model = EmpresaCliente
        fields = ['razao_social', 'nome_fantasia', 'cnpj', 'setor', 'porte', 'website', 'observacoes']
        widgets = {
            'razao_social': forms.TextInput(attrs={'class': 'form-control'}),
            'nome_fantasia': forms.TextInput(attrs={'class': 'form-control'}),
            'cnpj': forms.TextInput(attrs={'class': 'form-control'}),
            'setor': forms.TextInput(attrs={'class': 'form-control'}),
            'porte': forms.Select(attrs={'class': 'form-select'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'observacoes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class ContatoForm(forms.ModelForm):
    class Meta:
        model = Contato
        fields = ['empresa', 'nome', 'cargo', 'email', 'telefone', 'decisor']
