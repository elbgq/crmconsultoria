# projetos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from oportunidades.models import Oportunidade
from django.db.models.signals import post_delete
from .models import LancamentoHoras, ProjetoConsultoria, recalcular_horas_projeto


@receiver(post_save, sender=Oportunidade)
def criar_projeto_ao_ganhar(sender, instance, **kwargs):
    if instance.estagio == 'ganho' and not hasattr(instance, 'projeto'):
        ProjetoConsultoria.objects.create(
            oportunidade_origem=instance,
            nome=f"Projeto — {instance.titulo}",
            horas_estimadas=instance.horas_estimadas,
            data_inicio_real=instance.data_fechamento_real,
        )
    


@receiver([post_save, post_delete], sender=LancamentoHoras)
def atualizar_horas_do_projeto(sender, instance, **kwargs):
    recalcular_horas_projeto(instance.projeto_id)
