# crm_core/models.py
from django.db import models

# Estes models são utilizados em todo o sistema, como modelos base
# e enums para estágios do funil de vendas.    
class ModeloBase(models.Model):
    """Model abstrato com campos de auditoria comuns"""
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class EstagioFunil(models.TextChoices):
    PROSPECCAO = 'prospeccao', 'Prospecção'
    QUALIFICACAO = 'qualificacao', 'Qualificação'
    PROPOSTA = 'proposta', 'Proposta Enviada'
    NEGOCIACAO = 'negociacao', 'Negociação'
    GANHO = 'ganho', 'Ganho'
    PERDIDO = 'perdido', 'Perdido'

class TipoContrato(models.TextChoices):
    PROJETO_FECHADO = 'projeto', 'Projeto com Escopo Fechado'
    HORAS = 'horas', 'Banco de Horas'
    RETAINER = 'retainer', 'Retainer Mensal'
    SUCESSO = 'sucesso', 'Fee de Êxito / Performance'


class AreaConsultoria(models.TextChoices):
    ESTRATEGIA = 'estrategia', 'Estratégia'
    FINANCEIRA = 'financeira', 'Gestão Financeira'
    PROCESSOS = 'processos', 'Processos e Eficiência'
    RH = 'rh', 'Gestão de Pessoas'
    COMERCIAL = 'comercial', 'Comercial e Vendas'
    TI = 'ti', 'Transformação Digital'
    