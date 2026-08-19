# tarefas/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Tarefa


@receiver(pre_save, sender=Tarefa)
def marcar_data_conclusao(sender, instance, **kwargs):
    if instance.concluida and not instance.data_conclusao:
        instance.data_conclusao = timezone.now()
    elif not instance.concluida:
        instance.data_conclusao = None
    