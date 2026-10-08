import json

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from clientes.models import EmpresaCliente
from oportunidades.models import Oportunidade
from projetos.models import ProjetoConsultoria


def criar_oportunidade(usuario, **extra):
    empresa = EmpresaCliente.objects.create(razao_social='Empresa Teste')
    dados = dict(
        titulo='Diagnóstico', empresa_cliente=empresa, consultor_responsavel=usuario,
        area='estrategia', tipo_contrato='projeto', valor_estimado=1000, horas_estimadas=40,
    )
    dados.update(extra)
    return Oportunidade.objects.create(**dados)


def post_json(client, url, dados):
    return client.post(url, json.dumps(dados), content_type='application/json')


class HistoricoEEstagioTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.client.force_login(self.usuario)
        self.op = criar_oportunidade(self.usuario)

    def test_criacao_gera_um_registro_inicial(self):
        self.assertEqual(self.op.historico.count(), 1)
        self.assertIsNone(self.op.historico.get().estagio_anterior)

    def test_kanban_ajax_gera_um_unico_historico_com_autor(self):
        resp = post_json(self.client, reverse('oportunidades:atualizar_estagio_ajax'),
                         {'oportunidade_id': self.op.pk, 'novo_estagio': 'qualificacao'})
        self.assertEqual(resp.status_code, 200)
        mudancas = self.op.historico.filter(estagio_novo='qualificacao')
        self.assertEqual(mudancas.count(), 1)
        self.assertEqual(mudancas.get().alterado_por, self.usuario)

    def test_view_mudar_estagio_gera_um_unico_historico(self):
        post_json(self.client, reverse('oportunidades:mudar_estagio', args=[self.op.pk]),
                  {'estagio': 'proposta'})
        self.assertEqual(self.op.historico.filter(estagio_novo='proposta').count(), 1)

    def test_estagio_invalido_e_rejeitado(self):
        resp = post_json(self.client, reverse('oportunidades:atualizar_estagio_ajax'),
                         {'oportunidade_id': self.op.pk, 'novo_estagio': 'xyz'})
        self.assertEqual(resp.status_code, 400)

    def test_perdido_grava_motivo(self):
        post_json(self.client, reverse('oportunidades:atualizar_estagio_ajax'),
                  {'oportunidade_id': self.op.pk, 'novo_estagio': 'perdido', 'motivo_perda': 'preco'})
        self.op.refresh_from_db()
        self.assertEqual(self.op.motivo_perda, 'preco')


class ProjetoAutomaticoTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user('ana', password='x')
        self.client.force_login(self.usuario)

    def test_ganhar_cria_exatamente_um_projeto(self):
        op = criar_oportunidade(self.usuario)
        post_json(self.client, reverse('oportunidades:atualizar_estagio_ajax'),
                  {'oportunidade_id': op.pk, 'novo_estagio': 'ganho'})
        self.assertEqual(ProjetoConsultoria.objects.filter(oportunidade_origem=op).count(), 1)
        projeto = ProjetoConsultoria.objects.get(oportunidade_origem=op)
        self.assertEqual(projeto.nome, 'Projeto — Diagnóstico')
        self.assertEqual(projeto.horas_estimadas, 40)

    def test_salvar_novamente_nao_duplica_projeto(self):
        op = criar_oportunidade(self.usuario, estagio='ganho')
        op.save()
        op.save()
        self.assertEqual(ProjetoConsultoria.objects.count(), 1)


class ValidacaoTests(TestCase):
    def test_probabilidade_acima_de_100_e_invalida(self):
        usuario = User.objects.create_user('ana', password='x')
        op = criar_oportunidade(usuario)
        op.probabilidade = 150
        with self.assertRaises(ValidationError):
            op.full_clean()
