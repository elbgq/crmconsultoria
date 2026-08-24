from django.db import models
from django.conf import settings
from crm_core.models import ModeloBase, EstagioFunil, TipoContrato, AreaConsultoria
from clientes.models import EmpresaCliente, Contato


class Oportunidade(ModeloBase):
    titulo = models.CharField(max_length=200)
    empresa_cliente = models.ForeignKey(EmpresaCliente, on_delete=models.CASCADE, related_name='oportunidades')
    contato_principal = models.ForeignKey(Contato, on_delete=models.SET_NULL, null=True, blank=True)
    consultor_responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='oportunidades'
    )

    area = models.CharField(max_length=20, choices=AreaConsultoria.choices)
    tipo_contrato = models.CharField(max_length=20, choices=TipoContrato.choices)

    valor_estimado = models.DecimalField(max_digits=12, decimal_places=2)
    horas_estimadas = models.PositiveIntegerField(null=True, blank=True)
    valor_hora = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)

    probabilidade = models.PositiveSmallIntegerField(default=0)
    estagio = models.CharField(max_length=20, choices=EstagioFunil.choices, default=EstagioFunil.PROSPECCAO)
    origem = models.CharField(max_length=100, blank=True)

    data_inicio_prevista = models.DateField(null=True, blank=True)
    duracao_estimada_semanas = models.PositiveIntegerField(null=True, blank=True)
    data_fechamento_real = models.DateField(null=True, blank=True)

    motivo_perda = models.CharField(max_length=200, blank=True)
    observacoes = models.TextField(blank=True)

    class Meta: # type: ignore
        verbose_name = "Oportunidade"
        verbose_name_plural = "Oportunidades"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['estagio']),
            models.Index(fields=['consultor_responsavel', 'estagio']),
            models.Index(fields=['data_fechamento_real']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.empresa_cliente}"


class HistoricoEstagio(models.Model):
    oportunidade = models.ForeignKey(Oportunidade, on_delete=models.CASCADE, related_name='historico')
    estagio_anterior = models.CharField(max_length=20, choices=EstagioFunil.choices, null=True, blank=True)
    estagio_novo = models.CharField(max_length=20, choices=EstagioFunil.choices)
    data_mudanca = models.DateTimeField(auto_now_add=True)
    alterado_por = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = "Histórico de Estágio"
        verbose_name_plural = "Históricos de Estágio"
        ordering = ['-data_mudanca']

    def __str__(self):
        return f"{self.oportunidade.titulo}: {self.estagio_anterior} → {self.estagio_novo}"
    
    def save(self, *args, **kwargs):
        criando = self.pk is None  # só cria projeto na primeira gravação do histórico
        super().save(*args, **kwargs)

        # Se o novo estágio é "ganho", cria o projeto
        if criando and self.estagio_novo == 'ganho':
            oportunidade = self.oportunidade

            # Evita duplicação
            if not hasattr(oportunidade, 'projeto'):
                from projetos.models import ProjetoConsultoria, StatusProjeto

                ProjetoConsultoria.objects.create(
                    oportunidade_origem=oportunidade,
                    nome=f"Projeto — {oportunidade.titulo}",
                    status=StatusProjeto.NAO_INICIADO,
                    data_inicio_real=oportunidade.data_fechamento_real or None
                )
