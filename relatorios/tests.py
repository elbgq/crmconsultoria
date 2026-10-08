from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class PermissaoDashboardTests(TestCase):
    def logar(self, cargo=None, **kw):
        u = User.objects.create_user('u', password='x', **kw)
        if cargo:
            u.perfil.cargo = cargo
            u.perfil.save()
        self.client.force_login(u)

    def test_anonimo_vai_para_login(self):
        self.assertEqual(self.client.get(reverse('relatorios:dashboard')).status_code, 302)

    def test_consultor_recebe_403(self):
        self.logar('consultor')
        self.assertEqual(self.client.get(reverse('relatorios:dashboard')).status_code, 403)

    def test_socio_e_senior_acessam(self):
        for cargo in ('socio', 'consultor_senior'):
            self.client.logout()
            User.objects.all().delete()
            self.logar(cargo)
            self.assertEqual(self.client.get(reverse('relatorios:dashboard')).status_code, 200)

    def test_superusuario_acessa(self):
        self.logar(is_superuser=True)
        self.assertEqual(self.client.get(reverse('relatorios:dashboard')).status_code, 200)
