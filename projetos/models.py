from django.db import models
from django.conf import settings
from crm_core.models import ModeloBase
from oportunidades.models import Oportunidade
from django.utils import timezone


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
    horas_consumidas = models.DecimalField(max_digits=8, decimal_places=2, default=None, null=True, blank=True)

    observacoes = models.TextField(blank=True)

    class Meta: # type: ignore
        verbose_name = "Projeto de Consultoria"
        verbose_name_plural = "Projetos de Consultoria"
        ordering = ['-criado_em']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['gerente_projeto', 'status']),
        ]

    def __str__(self):
        return f"{self.nome} ({self.oportunidade_origem.empresa_cliente})" # type: ignore

    # Propriedade que calcula o percentual de horas consumidas em relação às horas estimadas
    @property
    def percentual_horas_consumidas(self):
        if not self.horas_estimadas:
            return None
        return round((float(self.horas_consumidas) / self.horas_estimadas) * 100, 1)         # type: ignore

    # Propriedade que calcula o progresso do projeto com base nas entregas
    @property
    def progresso(self):
        total = self.entregas.count() # type: ignore
        if total == 0:
            return 0
        concluidas = self.entregas.filter(concluida=True).count() # type: ignore
        return round((concluidas / total) * 100, 1)
    
    # Propriedade que calcula o status automático do projeto com base nas entregas
    @property
    def status_automatico(self):
        total = self.entregas.count() # type: ignore
        concluidas = self.entregas.filter(concluida=True).count() # type: ignore
        atrasadas = self.entregas.filter(concluida=False, data_prevista__lt=timezone.now().date()).count() # type: ignore

        if total == 0:
            return "Não Iniciado"
        if concluidas == total:
            return "Concluído"
        if atrasadas > 0:
            return "Atrasado"
        return "Em Andamento"
    
    # Para alertas automáticos das entregas/fases no detalhe do projeto.
    @property
    def fases_atrasadas(self):
        return self.entregas.filter( # type: ignore
            concluida=False,
            data_prevista__lt=timezone.now().date()
        )

    @property
    def fases_pendentes(self):
        return self.entregas.filter( # type: ignore
            concluida=False,
            data_prevista__gte=timezone.now().date()
        )

    @property
    def fases_concluidas(self):
        return self.entregas.filter(concluida=True) # type: ignore

    def atualizar_status(self):
        total = self.entregas.count() # type: ignore
        concluidas = self.entregas.filter(concluida=True).count() # type: ignore
        atrasadas = self.entregas.filter( # type: ignore
            concluida=False,
            data_prevista__lt=timezone.now().date()
        ).count()

        if total == 0:
            novo_status = StatusProjeto.NAO_INICIADO

        elif concluidas == total:
            novo_status = StatusProjeto.CONCLUIDO

        elif atrasadas > 0:
            novo_status = StatusProjeto.PAUSADO  # ou "Atrasado", se você quiser criar esse status

        else:
            novo_status = StatusProjeto.EM_ANDAMENTO

        # Atualiza apenas se mudou
        if self.status != novo_status:
            self.status = novo_status
            self.save(update_fields=['status'])

    @property
    def cor_status(self):
        mapa = {
            'nao_iniciado': 'secondary',
            'andamento': 'primary',
            'pausado': 'warning',
            'atrasado': 'danger',
            'concluido': 'success',
            'cancelado': 'secondary',
        }
        return mapa.get(self.status, 'secondary')



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

    class Meta: # type: ignore
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
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.projeto.atualizar_status()
    
    @property
    def cor_status(self):
        if self.concluida:
            return "success"
        if self.atrasada:
            return "danger"
        return "warning"

