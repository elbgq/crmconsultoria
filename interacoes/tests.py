from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from clientes.models import Contato
from interacoes.models import Interacao
from oportunidades.tests import criar_oportunidade


class InteracaoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.client.force_login(self.usuario)
        self.op = criar_oportunidade(self.usuario)
        self.contato = Contato.objects.create(empresa=self.op.empresa_cliente, nome='Maria')

    def dados(self, **extra):
        d = {
            'contato': self.contato.pk, 'tipo': 'ligacao', 'assunto': 'Primeiro contato',
            'data_interacao': timezone.localtime().strftime('%d/%m/%Y %H:%M'),
        }
        d.update(extra)
        return d

    def test_registrar_pelo_contato_define_responsavel(self):
        resp = self.client.post(reverse('interacoes:registrar', args=[self.contato.pk]), self.dados())
        self.assertRedirects(resp, reverse('clientes:detalhe_contato', args=[self.contato.pk]))
        i = Interacao.objects.get()
        self.assertEqual(i.responsavel, self.usuario)
        self.assertEqual(i.contato, self.contato)
        self.assertIsNone(i.oportunidade)

    def test_registrar_pela_oportunidade_vincula_a_oportunidade(self):
        resp = self.client.post(reverse('interacoes:nova_interacao_oportunidade', args=[self.op.pk]),
                                self.dados(tipo='reuniao'))
        self.assertRedirects(resp, reverse('oportunidades:detalhe', args=[self.op.pk]))
        self.assertEqual(Interacao.objects.get().oportunidade, self.op)

    def test_assunto_obrigatorio(self):
        resp = self.client.post(reverse('interacoes:registrar', args=[self.contato.pk]),
                                self.dados(assunto=''))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(Interacao.objects.exists())

    def test_editar_e_excluir(self):
        i = Interacao.objects.create(contato=self.contato, tipo='email', assunto='A',
                                     data_interacao=timezone.now(), responsavel=self.usuario)
        self.client.post(reverse('interacoes:editar', args=[i.pk]), self.dados(assunto='B', tipo='email'))
        i.refresh_from_db()
        self.assertEqual(i.assunto, 'B')
        url = reverse('interacoes:excluir', args=[i.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Interacao.objects.exists())
        self.client.post(url)
        self.assertFalse(Interacao.objects.exists())

    def test_excluir_oportunidade_preserva_interacao(self):
        i = Interacao.objects.create(contato=self.contato, oportunidade=self.op, tipo='email',
                                     assunto='A', data_interacao=timezone.now())
        self.op.delete()
        i.refresh_from_db()
        self.assertIsNone(i.oportunidade)

    def test_excluir_contato_apaga_interacoes(self):
        Interacao.objects.create(contato=self.contato, tipo='email', assunto='A',
                                 data_interacao=timezone.now())
        self.contato.delete()
        self.assertFalse(Interacao.objects.exists())

    def test_anonimo_vai_para_login(self):
        self.client.logout()
        resp = self.client.get(reverse('interacoes:registrar', args=[self.contato.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)
