from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from usuarios.models import Cargo, Perfil
from usuarios.permissions import eh_consultor_senior_ou_socio, eh_socio


class PerfilETests(TestCase):
    def test_perfil_criado_automaticamente_com_cargo_consultor(self):
        u = User.objects.create_user('ana', password='x')
        self.assertEqual(u.perfil.cargo, Cargo.CONSULTOR)
        self.assertEqual(Perfil.objects.filter(usuario=u).count(), 1)

    def test_atualizar_usuario_nao_cria_outro_perfil(self):
        u = User.objects.create_user('ana', password='x')
        u.first_name = 'Ana'
        u.save()
        self.assertEqual(Perfil.objects.count(), 1)

    def test_funcoes_de_permissao_por_cargo(self):
        u = User.objects.create_user('ana', password='x')
        self.assertFalse(eh_socio(u))
        self.assertFalse(eh_consultor_senior_ou_socio(u))
        u.perfil.cargo = Cargo.CONSULTOR_SENIOR
        self.assertTrue(eh_consultor_senior_ou_socio(u))
        self.assertFalse(eh_socio(u))
        u.perfil.cargo = Cargo.SOCIO
        self.assertTrue(eh_socio(u))


class LoginTests(TestCase):
    def setUp(self):
        User.objects.create_user('ana', password='segredo123')

    def test_login_valido_redireciona_para_home(self):
        resp = self.client.post(reverse('login'), {'username': 'ana', 'password': 'segredo123'})
        self.assertRedirects(resp, reverse('crm_core:home'))

    def test_login_invalido_permanece_na_tela(self):
        resp = self.client.post(reverse('login'), {'username': 'ana', 'password': 'errada'})
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(resp.wsgi_request.user.is_authenticated)

    def test_logout_por_post(self):
        self.client.login(username='ana', password='segredo123')
        self.client.post(reverse('logout'))
        self.assertEqual(self.client.get(reverse('crm_core:home')).status_code, 302)

    def test_paginas_internas_exigem_login(self):
        for nome in ('crm_core:home', 'clientes:lista', 'oportunidades:lista', 'oportunidades:kanban',
                     'projetos:lista', 'tarefas:tarefas_lista', 'relatorios:dashboard'):
            resp = self.client.get(reverse(nome))
            self.assertEqual(resp.status_code, 302, nome)
            self.assertIn('/login/', resp.url, nome)


class LinkRelatoriosNaNavbarTests(TestCase):
    def home(self, cargo=None, **kw):
        u = User.objects.create_user('u', password='x', **kw)
        if cargo:
            u.perfil.cargo = cargo
            u.perfil.save()
        self.client.force_login(u)
        return self.client.get(reverse('crm_core:home')).content.decode()

    def test_consultor_nao_ve_link(self):
        self.assertNotIn(reverse('relatorios:dashboard'), self.home('consultor'))

    def test_socio_senior_e_superusuario_veem_link(self):
        for i, (cargo, kw) in enumerate([('socio', {}), ('consultor_senior', {}), (None, {'is_superuser': True})]):
            User.objects.all().delete()
            self.client.logout()
            self.assertIn(reverse('relatorios:dashboard'), self.home(cargo, **kw), i)
