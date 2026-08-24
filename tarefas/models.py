from django.db import models
from django.conf import settings
from django.utils import timezone
from crm_core.models import ModeloBase
from oportunidades.models import Oportunidade
from projetos.models import ProjetoConsultoria
from django.core.exceptions import ValidationError


class PrioridadeTarefa(models.TextChoices):
    BAIXA = 'baixa', 'Baixa'
    MEDIA = 'media', 'Média'
    ALTA = 'alta', 'Alta'
    URGENTE = 'urgente', 'Urgente'


class TipoTarefa(models.TextChoices):
    LIGACAO = 'ligacao', 'Ligação'
    EMAIL = 'email', 'E-mail'
    REUNIAO = 'reuniao', 'Reunião'
    ENTREGA = 'entrega', 'Entrega Interna'
    OUTRO = 'outro', 'Outro'


class Tarefa(ModeloBase):
    titulo = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    tipo = models.CharField(max_length=20, choices=TipoTarefa.choices, default=TipoTarefa.OUTRO)
    prioridade = models.CharField(max_length=20, choices=PrioridadeTarefa.choices, default=PrioridadeTarefa.MEDIA)
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='tarefas')
    # Vínculos opcionais — uma tarefa pertence a UM dos dois (ou a nenhum)
    oportunidade = models.ForeignKey(
        Oportunidade, on_delete=models.CASCADE, null=False, blank=False, related_name='tarefas'
    )
    projeto = models.ForeignKey(
        ProjetoConsultoria, on_delete=models.CASCADE, null=True, blank=True, related_name='tarefas')
    data_vencimento = models.DateTimeField()
    concluida = models.BooleanField(default=False)
    data_conclusao = models.DateTimeField(null=True, blank=True)


    class Meta(ModeloBase.Meta):
        verbose_name = "Tarefa"
        verbose_name_plural = "Tarefas"
        ordering = ['data_vencimento']
        indexes = [
            models.Index(fields=['responsavel', 'concluida']),
            models.Index(fields=['data_vencimento']),
        ]

    def __str__(self):
        return self.titulo

    @property
    def atrasada(self):
        if self.concluida:
            return False
        return self.data_vencimento < timezone.now()

    @property
    def vinculo(self):
        """Retorna a que a tarefa está relacionada, se houver."""
        if self.projeto:
            return self.projeto
        if self.oportunidade:
            return self.oportunidade
        return None
    
    def clean(self):
        if self.oportunidade and self.projeto:
            raise ValidationError("Uma tarefa deve estar vinculada a apenas uma Oportunidade OU um Projeto, não ambos.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
    