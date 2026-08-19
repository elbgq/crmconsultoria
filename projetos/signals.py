# projetos/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from oportunidades.models import Oportunidade
from .models import ProjetoConsultoria


@receiver(post_save, sender=Oportunidade)
def criar_projeto_ao_ganhar(sender, instance, **kwargs):
    if instance.estagio == 'ganho' and not hasattr(instance, 'projeto'):
        ProjetoConsultoria.objects.create(
            oportunidade_origem=instance,
            nome=instance.titulo,
            horas_estimadas=instance.horas_estimadas,
        )
    