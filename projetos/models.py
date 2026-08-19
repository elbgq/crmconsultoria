from django.db import models
from django.conf import settings
from crm_core.models import ModeloBase
from oportunidades.models import Oportunidade


class StatusProjeto(models.TextChoices):
    NAO_INICIADO = 'nao_iniciado', 'Não Iniciado'
    EM_ANDAMENTO = 'andamento', 'Em Andamento'
    PAUSADO = 'pausado', 'Pausado'
    CONCLUIDO = 'concluido', 'Concluído'
    CANCELADO = 'cancelado', 'Cancelado'


class ProjetoConsultoria(ModeloBase):
    oportunidade_origem = models.OneToOneField(
        Oportunidade, on_delete=models.CASCADE, related_name='projeto'
    )
    nome = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=StatusProjeto.choices, default=StatusProjeto.NAO_INICIADO)

    equipe = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='projetos', blank=True)
    gerente_projeto = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
        related_name='projetos_gerenciados'
    )

    data_inicio_real = models.DateField(null=True, blank=True)
    data_fim_prevista = models.DateField(null=True, blank=True)
    data_fim_real = models.DateField(null=True, blank=True)

    horas_estimadas = models.PositiveIntegerField(null=True, blank=True)
    horas_consumidas = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    observacoes = models.TextField(blank=True)

    class Meta:
        verbose_name = "Projeto de Consultoria"
        verbose_name_plural = "Projetos de Consultoria"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['gerente_projeto', 'status']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.oportunidade_origem.empresa_cliente})"

    @property
    def percentual_horas_consumidas(self):
        if not self.horas_estimadas:
            return None
        return round((float(self.horas_consumidas) / self.horas_estimadas) * 100, 1)


class Entrega(ModeloBase):
    """Marcos/deliverables do projeto — diagnóstico, plano de ação, relatório final etc."""
    projeto = models.ForeignKey(ProjetoConsultoria, on_delete=models.CASCADE, related_name='entregas')
    nome = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_prevista = models.DateField()
    data_entregue = models.DateField(null=True, blank=True)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='entregas'
    )
    concluida = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Entrega"
        verbose_name_plural = "Entregas"
        ordering = ['data_prevista']

    def __str__(self):
        return f"{self.nome} — {self.projeto.nome}"

    @property
    def atrasada(self):
        from django.utils import timezone
        if self.concluida:
            return False
        return self.data_prevista < timezone.now().date()
    