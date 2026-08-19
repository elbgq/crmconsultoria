from django.db import models
from crm_core.models import ModeloBase


class EmpresaCliente(ModeloBase):
    class Porte(models.TextChoices):
        MEI = 'mei', 'MEI'
        PEQUENA = 'pequena', 'Pequena'
        MEDIA = 'media', 'Média'
        GRANDE = 'grande', 'Grande'

    class Modalidade(models.TextChoices):
        COMPRADOR = 'comprador', 'Comprador'
        VENDEDOR = 'vendedor', 'Vendedor'

    razao_social = models.CharField(max_length=200)
    nome_fantasia = models.CharField(max_length=200, blank=True)
    cnpj = models.CharField(max_length=18, blank=True)
    setor = models.CharField(max_length=100, blank=True)
    porte = models.CharField(max_length=20, choices=Porte.choices, blank=True)
    website = models.URLField(blank=True)
    modalidade = models.CharField(
        max_length=20,
        choices=Modalidade.choices,
        default=Modalidade.VENDEDOR,
        blank=True,
    )
    observacoes = models.TextField(blank=True)

    class Meta: # type: ignore
        verbose_name = "Empresa Cliente"
        verbose_name_plural = "Empresas Clientes"
        ordering = ['razao_social']

    def __str__(self):
        return self.nome_fantasia or self.razao_social


class Contato(ModeloBase):
    empresa = models.ForeignKey(EmpresaCliente, on_delete=models.CASCADE, related_name='contatos')
    nome = models.CharField(max_length=150)
    cargo = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    telefone = models.CharField(max_length=20, blank=True)
    decisor = models.BooleanField(default=False)

    class Meta: # type: ignore
        verbose_name = "Contato"
        verbose_name_plural = "Contatos"
        ordering = ['nome']

    def __str__(self):
        return f"{self.nome} ({self.empresa.nome_fantasia or self.empresa.razao_social})"
    