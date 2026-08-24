# oportunidades/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Oportunidade, HistoricoEstagio

# Detalhe importante: signal para registrar o histórico automaticamente

# Para não depender de lembrar de criar o HistoricoEstagio manualmente em
# toda view, vale automatizar com este signal.

@receiver(pre_save, sender=Oportunidade)
def registrar_mudanca_estagio(sender, instance, **kwargs):
    if not instance.pk:
        return  # objeto novo, ainda não tem estágio "anterior"

    anterior = Oportunidade.objects.filter(pk=instance.pk).values_list('estagio', flat=True).first()
    if anterior and anterior != instance.estagio:
        instance._estagio_mudou = (anterior, instance.estagio)


from django.db.models.signals import post_save

@receiver(post_save, sender=Oportunidade)
def salvar_historico(sender, instance, created, **kwargs):
    if created:
        HistoricoEstagio.objects.create(estagio_anterior=None, estagio_novo=instance.estagio, oportunidade=instance)
    elif hasattr(instance, '_estagio_mudou'):
        anterior, novo = instance._estagio_mudou
        HistoricoEstagio.objects.create(estagio_anterior=anterior, estagio_novo=novo, oportunidade=instance)
        