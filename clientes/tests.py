from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from clientes.models import Contato, EmpresaCliente


class ClientesTestCase(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.client.force_login(self.usuario)
        self.empresa = EmpresaCliente.objects.create(razao_social='Alfa Ltda', nome_fantasia='Alfa')
        self.contato = Contato.objects.create(empresa=self.empresa, nome='Maria')


class EmpresaTests(ClientesTestCase):
    def test_lista_e_busca_por_razao_social_e_fantasia(self):
        EmpresaCliente.objects.create(razao_social='Beta SA', nome_fantasia='Gama')
        url = reverse('clientes:lista')
        self.assertContains(self.client.get(url), 'Beta SA')
        resp = self.client.get(url, {'busca': 'Alfa'})
        self.assertContains(resp, 'Alfa Ltda')
        self.assertNotContains(resp, 'Beta SA')
        self.assertContains(self.client.get(url, {'busca': 'Gama'}), 'Beta SA')

    def test_criar_empresa(self):
        resp = self.client.post(reverse('clientes:criar'), {'razao_social': 'Nova Ltda', 'porte': 'mei'})
        self.assertEqual(resp.status_code, 302)
        self.assertTrue(EmpresaCliente.objects.filter(razao_social='Nova Ltda').exists())

    def test_criar_empresa_sem_razao_social_e_invalido(self):
        resp = self.client.post(reverse('clientes:criar'), {'razao_social': ''})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(EmpresaCliente.objects.count(), 1)

    def test_detalhe_e_edicao(self):
        self.assertEqual(self.client.get(reverse('clientes:detalhe', args=[self.empresa.pk])).status_code, 200)
        self.client.post(reverse('clientes:editar', args=[self.empresa.pk]),
                         {'razao_social': 'Alfa Editada', 'porte': ''})
        self.empresa.refresh_from_db()
        self.assertEqual(self.empresa.razao_social, 'Alfa Editada')

    def test_excluir_empresa_apaga_contatos(self):
        self.client.post(reverse('clientes:excluir', args=[self.empresa.pk]))
        self.assertFalse(EmpresaCliente.objects.exists())
        self.assertFalse(Contato.objects.exists())


class ContatoTests(ClientesTestCase):
    def test_criar_contato(self):
        resp = self.client.post(reverse('clientes:criar_contato', args=[self.empresa.pk]),
                                {'empresa': self.empresa.pk, 'nome': 'João', 'decisor': 'on'})
        self.assertRedirects(resp, reverse('clientes:detalhe', args=[self.empresa.pk]))
        self.assertTrue(Contato.objects.get(nome='João').decisor)

    def test_editar_contato(self):
        self.client.post(reverse('clientes:editar_contato', args=[self.contato.pk]),
                         {'empresa': self.empresa.pk, 'nome': 'Maria Silva'})
        self.contato.refresh_from_db()
        self.assertEqual(self.contato.nome, 'Maria Silva')

    def test_excluir_contato_pede_confirmacao_e_exclui_no_post(self):
        url = reverse('clientes:excluir_contato', args=[self.contato.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(Contato.objects.exists())
        self.client.post(url)
        self.assertFalse(Contato.objects.exists())

    def test_ajax_contatos_por_empresa(self):
        outra = EmpresaCliente.objects.create(razao_social='Outra')
        Contato.objects.create(empresa=outra, nome='Zé')
        resp = self.client.get(reverse('clientes:ajax_contatos_por_empresa'), {'empresa_id': self.empresa.pk})
        nomes = [c['nome'] for c in resp.json()]
        self.assertEqual(len(nomes), 1)
        self.assertIn('Maria', nomes[0])

    def test_ajax_sem_empresa_retorna_lista_vazia(self):
        self.assertEqual(self.client.get(reverse('clientes:ajax_contatos_por_empresa')).json(), [])


class AcessoAnonimoTests(TestCase):
    def test_telas_redirecionam_para_login(self):
        self.client.logout()
        for nome in ('clientes:lista', 'clientes:criar'):
            resp = self.client.get(reverse(nome))
            self.assertEqual(resp.status_code, 302, nome)
            self.assertIn('/login/', resp.url)
