from datetime import timedelta

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
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


class TarefaViewsTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.outro = User.objects.create_user('beto', password='x')
        self.client.force_login(self.usuario)
        self.op = criar_oportunidade(self.usuario)
        self.projeto = ProjetoConsultoria.objects.create(oportunidade_origem=self.op, nome='P')
        self.venc = timezone.now() + timedelta(days=1)

    def dados(self, **extra):
        d = {'titulo': 'Ligar', 'tipo': 'ligacao', 'prioridade': 'alta',
             'data_vencimento': self.venc.strftime('%d/%m/%Y %H:%M')}
        d.update(extra)
        return d

    def test_lista_mostra_so_tarefas_do_usuario(self):
        Tarefa.objects.create(titulo='Minha', responsavel=self.usuario, data_vencimento=self.venc)
        Tarefa.objects.create(titulo='Do outro', responsavel=self.outro, data_vencimento=self.venc)
        resp = self.client.get(reverse('tarefas:tarefas_lista'))
        self.assertContains(resp, 'Minha')
        self.assertNotContains(resp, 'Do outro')

    def test_criar_a_partir_da_oportunidade(self):
        url = reverse('tarefas:tarefa_nova') + f'?oportunidade={self.op.pk}'
        self.assertEqual(self.client.get(url).status_code, 200)
        self.client.post(url, self.dados(oportunidade=self.op.pk))
        t = Tarefa.objects.get(titulo='Ligar')
        self.assertEqual(t.oportunidade, self.op)
        self.assertIsNone(t.projeto)

    def test_criar_a_partir_do_projeto_nao_exige_oportunidade(self):
        url = reverse('tarefas:tarefa_nova') + f'?projeto={self.projeto.pk}'
        self.client.post(url, self.dados(projeto=self.projeto.pk))
        t = Tarefa.objects.get(titulo='Ligar')
        self.assertEqual(t.projeto, self.projeto)
        self.assertIsNone(t.oportunidade)

    def test_editar_tarefa(self):
        t = Tarefa.objects.create(titulo='Antes', responsavel=self.usuario, data_vencimento=self.venc,
                                  oportunidade=self.op)
        self.client.post(reverse('tarefas:tarefa_editar', args=[t.pk]),
                         self.dados(titulo='Depois', oportunidade=self.op.pk))
        t.refresh_from_db()
        self.assertEqual(t.titulo, 'Depois')

    def test_concluir_redireciona_para_a_oportunidade(self):
        t = Tarefa.objects.create(titulo='T', responsavel=self.usuario, data_vencimento=self.venc,
                                  oportunidade=self.op)
        resp = self.client.get(reverse('tarefas:tarefa_concluir', args=[t.pk]))
        self.assertRedirects(resp, reverse('oportunidades:detalhe', args=[self.op.pk]))
        t.refresh_from_db()
        self.assertTrue(t.concluida)
        self.assertIsNotNone(t.data_conclusao)

    def test_concluir_tarefa_de_projeto_volta_para_o_projeto(self):
        t = Tarefa.objects.create(titulo='T', responsavel=self.usuario, data_vencimento=self.venc,
                                  projeto=self.projeto)
        resp = self.client.get(reverse('tarefas:tarefa_concluir', args=[t.pk]))
        self.assertRedirects(resp, reverse('projetos:detalhe', args=[self.projeto.pk]))
