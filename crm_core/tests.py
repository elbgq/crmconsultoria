from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clientes.models import EmpresaCliente
from oportunidades.tests import criar_oportunidade


class HomeTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.client.force_login(self.usuario)

    def test_home_conta_empresas_e_oportunidades_abertas(self):
        criar_oportunidade(self.usuario)
        criar_oportunidade(self.usuario, estagio='perdido')
        ctx = self.client.get(reverse('crm_core:home')).context
        self.assertEqual(ctx['total_empresas'], EmpresaCliente.objects.count())
        self.assertEqual(ctx['total_oportunidades_abertas'], 1)
        self.assertEqual(ctx['valor_em_negociacao'], 1000)

    def test_home_sem_dados(self):
        ctx = self.client.get(reverse('crm_core:home')).context
        self.assertEqual(ctx['total_oportunidades_abertas'], 0)
        self.assertEqual(ctx['valor_em_negociacao'], 0)
