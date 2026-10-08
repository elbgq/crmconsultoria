from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.utils import timezone

from oportunidades.tests import criar_oportunidade
from projetos.models import Entrega, ProjetoConsultoria, StatusProjeto


class ProjetoStatusTests(TestCase):
    def setUp(self):
        usuario = User.objects.create_user('ana', password='x')
        self.projeto = ProjetoConsultoria.objects.create(
            oportunidade_origem=criar_oportunidade(usuario), nome='P', horas_estimadas=100,
        )
        self.hoje = timezone.now().date()

    def test_percentual_com_horas_consumidas_nulas(self):
        self.assertIsNone(self.projeto.horas_consumidas)
        self.assertIsNone(self.projeto.percentual_horas_consumidas)

    def test_percentual_calculado(self):
        self.projeto.horas_consumidas = Decimal('25')
        self.assertEqual(self.projeto.percentual_horas_consumidas, 25.0)

    def test_entrega_atrasada_marca_projeto_atrasado(self):
        Entrega.objects.create(projeto=self.projeto, nome='E1', data_prevista=self.hoje - timedelta(days=2))
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.status, StatusProjeto.ATRASADO)

    def test_entrega_no_prazo_marca_em_andamento(self):
        Entrega.objects.create(projeto=self.projeto, nome='E1', data_prevista=self.hoje + timedelta(days=5))
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.status, StatusProjeto.EM_ANDAMENTO)

    def test_todas_concluidas_marca_concluido_e_progresso_100(self):
        e = Entrega.objects.create(projeto=self.projeto, nome='E1', data_prevista=self.hoje)
        e.concluida = True
        e.save()
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.status, StatusProjeto.CONCLUIDO)
        self.assertEqual(self.projeto.progresso, 100)
