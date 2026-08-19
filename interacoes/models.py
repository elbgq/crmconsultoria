# Esse módulo registra todo contato feito com o cliente — e-mails, ligações, reuniões
# — vinculado tanto ao Contato (pessoa) quanto, opcionalmente, à Oportunidade em andamento.
from django.db import models
from django.conf import settings
from crm_core.models import ModeloBase
from clientes.models import Contato
from oportunidades.models import Oportunidade


class TipoInteracao(models.TextChoices):
    LIGACAO = 'ligacao', 'Ligação'
    EMAIL = 'email', 'E-mail'
    REUNIAO = 'reuniao', 'Reunião'
    WHATSAPP = 'whatsapp', 'WhatsApp'
    VISITA = 'visita', 'Visita Presencial'
    OUTRO = 'outro', 'Outro'

# Por que oportunidade é opcional (null=True, blank=True)

# Nem toda interação está ligada a uma venda em andamento — pode ser um contato de relacionamento
# pós-venda, ou uma ligação de cortesia sem oportunidade aberta. Deixar opcional evita forçar um
# vínculo artificial.

# Por que on_delete=models.SET_NULL na oportunidade (diferente do CASCADE em contato)

# Se uma oportunidade for excluída, o histórico de interações não deveria desaparecer
# — ele tem valor por si só como registro de relacionamento com o cliente. Já se o Contato
# for excluído, não faz sentido manter interações "órfãs" sem ninguém para vincular.

class Interacao(ModeloBase):
    contato = models.ForeignKey(Contato, on_delete=models.CASCADE, related_name='interacoes')
    oportunidade = models.ForeignKey(
        Oportunidade, on_delete=models.SET_NULL, null=True, blank=True, related_name='interacoes'
    )
    responsavel = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='interacoes'
    )

    tipo = models.CharField(max_length=20, choices=TipoInteracao.choices)
    assunto = models.CharField(max_length=200)
    descricao = models.TextField(blank=True)
    data_interacao = models.DateTimeField()

    class Meta(ModeloBase.Meta):
        verbose_name = "Interação"
        verbose_name_plural = "Interações"
        ordering = ['-data_interacao']
        indexes = [
            models.Index(fields=['contato', '-data_interacao']),
            models.Index(fields=['oportunidade', '-data_interacao']),
        ]

    def __str__(self):
        return f"{self.get_tipo_display()} — {self.contato} ({self.data_interacao:%d/%m/%Y})"