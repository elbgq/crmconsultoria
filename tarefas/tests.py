from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

from oportunidades.tests import criar_oportunidade
from projetos.models import ProjetoConsultoria
from tarefas.models import Tarefa


class TarefaTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.op = criar_oportunidade(self.usuario)
        self.projeto = ProjetoConsultoria.objects.create(oportunidade_origem=self.op, nome='P')
        self.venc = timezone.now() + timedelta(days=1)

    def nova(self, **extra):
        return Tarefa.objects.create(titulo='T', responsavel=self.usuario, data_vencimento=self.venc, **extra)

    def test_tarefa_so_de_projeto(self):
        self.assertEqual(self.nova(projeto=self.projeto).vinculo, self.projeto)

    def test_tarefa_so_de_oportunidade(self):
        self.assertEqual(self.nova(oportunidade=self.op).vinculo, self.op)

    def test_tarefa_sem_vinculo_e_permitida(self):
        self.assertIsNone(self.nova().vinculo)

    def test_oportunidade_e_projeto_juntos_sao_rejeitados(self):
        with self.assertRaises(ValidationError):
            self.nova(oportunidade=self.op, projeto=self.projeto)

    def test_data_conclusao_preenchida_e_limpa(self):
        t = self.nova(oportunidade=self.op)
        t.concluida = True
        t.save()
        self.assertIsNotNone(t.data_conclusao)
        t.concluida = False
        t.save()
        self.assertIsNone(t.data_conclusao)

    def test_atrasada(self):
        t = self.nova(oportunidade=self.op)
        t.data_vencimento = timezone.now() - timedelta(hours=1)
        self.assertTrue(t.atrasada)
