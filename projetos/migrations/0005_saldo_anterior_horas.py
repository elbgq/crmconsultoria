from decimal import Decimal

from django.db import migrations

DESCRICAO = 'Saldo anterior ao lançamento de horas'
LIMITE = Decimal('24')


def criar_saldo_anterior(apps, schema_editor):
    """Projetos com horas digitadas à mão ganham lançamentos de saldo, para a soma não zerar."""
    Projeto = apps.get_model('projetos', 'ProjetoConsultoria')
    Lancamento = apps.get_model('projetos', 'LancamentoHoras')
    for projeto in Projeto.objects.filter(horas_consumidas__gt=0):
        restante = projeto.horas_consumidas
        data = projeto.criado_em.date()
        while restante > 0:
            parte = min(restante, LIMITE)
            Lancamento.objects.create(projeto=projeto, usuario=None, data=data, horas=parte, descricao=DESCRICAO)
            restante -= parte


def remover_saldo_anterior(apps, schema_editor):
    apps.get_model('projetos', 'LancamentoHoras').objects.filter(descricao=DESCRICAO).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('projetos', '0004_lancamento_horas'),
    ]

    operations = [
        migrations.RunPython(criar_saldo_anterior, remover_saldo_anterior),
    ]
