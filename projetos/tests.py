from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from oportunidades.tests import criar_oportunidade
from projetos.models import Entrega, LancamentoHoras, ProjetoConsultoria, StatusProjeto


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


class LancamentoBase(TestCase):
    """Preparação e helpers comuns aos testes de lançamento de horas."""

    def setUp(self):
        self.ana = User.objects.create_user('ana', password='x')
        self.beto = User.objects.create_user('beto', password='x')
        self.client.force_login(self.ana)
        self.projeto = ProjetoConsultoria.objects.create(
            oportunidade_origem=criar_oportunidade(self.ana), nome='P', horas_estimadas=100,
        )
        self.hoje = timezone.localdate()

    def lancar(self, horas='2.5', data=None, descricao='Reunião'):
        return self.client.post(
            reverse('projetos:lancar_horas', args=[self.projeto.pk]),
            {'data': (data or self.hoje).isoformat(), 'horas': horas, 'descricao': descricao},
        )

    def criar(self, usuario, horas, **extra):
        return LancamentoHoras.objects.create(projeto=self.projeto, usuario=usuario, data=self.hoje,
                                              horas=Decimal(horas), **extra)


class LancamentoHorasTests(LancamentoBase):
    def test_lancar_define_usuario_e_atualiza_horas_do_projeto(self):
        resp = self.lancar('2.5')
        self.assertRedirects(resp, reverse('projetos:detalhe', args=[self.projeto.pk]))
        self.assertEqual(LancamentoHoras.objects.get().usuario, self.ana)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('2.5'))
        self.assertEqual(self.projeto.percentual_horas_consumidas, 2.5)

    def test_soma_de_varios_lancamentos(self):
        self.criar(self.ana, '3')
        self.criar(self.beto, '4.25')
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('7.25'))

    def test_editar_recalcula(self):
        l = self.criar(self.ana, '3')
        self.client.post(reverse('projetos:editar_horas', args=[l.pk]),
                         {'data': self.hoje.isoformat(), 'horas': '5', 'descricao': ''})
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('5'))

    def test_excluir_recalcula_para_zero(self):
        l = self.criar(self.ana, '3')
        url = reverse('projetos:excluir_horas', args=[l.pk])
        self.assertEqual(self.client.get(url).status_code, 200)
        self.assertTrue(LancamentoHoras.objects.exists())
        self.client.post(url)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, 0)

    def test_validacoes_de_horas_e_data(self):
        for horas in ('0', '-1', '25', '0.1'):
            self.lancar(horas)
        self.lancar('2', data=self.hoje + timedelta(days=1))
        self.assertFalse(LancamentoHoras.objects.exists())

    def test_consultor_nao_edita_nem_exclui_lancamento_de_outro(self):
        l = self.criar(self.beto, '3')
        self.assertEqual(self.client.get(reverse('projetos:editar_horas', args=[l.pk])).status_code, 403)
        self.assertEqual(self.client.post(reverse('projetos:excluir_horas', args=[l.pk])).status_code, 403)
        self.assertTrue(LancamentoHoras.objects.exists())

    def test_socio_e_senior_gerenciam_lancamento_de_outro(self):
        l = self.criar(self.beto, '3')
        for cargo in ('socio', 'consultor_senior'):
            self.ana.perfil.cargo = cargo
            self.ana.perfil.save()
            self.ana.refresh_from_db()
            self.assertEqual(self.client.get(reverse('projetos:editar_horas', args=[l.pk])).status_code, 200)

    def test_detalhe_mostra_total_por_consultor_e_botoes_so_nos_proprios(self):
        self.criar(self.ana, '3', descricao='Meu')
        self.criar(self.beto, '2', descricao='Dele')
        resp = self.client.get(reverse('projetos:detalhe', args=[self.projeto.pk]))
        self.assertContains(resp, 'Meu')
        self.assertContains(resp, 'Dele')
        proprio = LancamentoHoras.objects.get(descricao='Meu')
        alheio = LancamentoHoras.objects.get(descricao='Dele')
        self.assertContains(resp, reverse('projetos:editar_horas', args=[proprio.pk]))
        self.assertNotContains(resp, reverse('projetos:editar_horas', args=[alheio.pk]))

    def test_excluir_usuario_preserva_lancamento(self):
        l = self.criar(self.beto, '3')
        self.beto.delete()
        l.refresh_from_db()
        self.assertIsNone(l.usuario)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('3'))

    def test_anonimo_vai_para_login(self):
        self.client.logout()
        resp = self.client.get(reverse('projetos:lancar_horas', args=[self.projeto.pk]))
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login/', resp.url)

    def test_formulario_do_projeto_nao_edita_horas_consumidas(self):
        resp = self.client.get(reverse('projetos:editar_projeto', args=[self.projeto.pk]))
        self.assertNotIn('horas_consumidas', resp.context['form'].fields)


class LancamentoPorFaseTests(LancamentoBase):
    def setUp(self):
        super().setUp()
        self.fase = Entrega.objects.create(projeto=self.projeto, nome='Diagnóstico', data_prevista=self.hoje)
        outro = ProjetoConsultoria.objects.create(
            oportunidade_origem=criar_oportunidade(self.ana), nome='Outro',
        )
        self.fase_alheia = Entrega.objects.create(projeto=outro, nome='Fase alheia', data_prevista=self.hoje)

    def dados(self, **extra):
        d = {'data': self.hoje.isoformat(), 'horas': '2', 'descricao': ''}
        d.update(extra)
        return d

    def url(self):
        return reverse('projetos:lancar_horas', args=[self.projeto.pk])

    def test_fase_e_opcional(self):
        self.client.post(self.url(), self.dados())
        self.assertIsNone(LancamentoHoras.objects.get().entrega)

    def test_lancar_horas_em_uma_fase(self):
        self.client.post(self.url(), self.dados(entrega=self.fase.pk, horas='3'))
        self.assertEqual(LancamentoHoras.objects.get().entrega, self.fase)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('3'))

    def test_fase_de_outro_projeto_e_rejeitada(self):
        resp = self.client.post(self.url(), self.dados(entrega=self.fase_alheia.pk))
        self.assertEqual(resp.status_code, 200)
        self.assertFalse(LancamentoHoras.objects.exists())

    def test_formulario_lista_so_fases_do_projeto(self):
        form = self.client.get(self.url()).context['form']
        self.assertEqual(list(form.fields['entrega'].queryset), [self.fase])

    def test_detalhe_mostra_horas_por_fase(self):
        LancamentoHoras.objects.create(projeto=self.projeto, usuario=self.ana, data=self.hoje,
                                       horas=Decimal('2'), entrega=self.fase)
        LancamentoHoras.objects.create(projeto=self.projeto, usuario=self.ana, data=self.hoje,
                                       horas=Decimal('1.5'), entrega=self.fase)
        entregas = list(self.client.get(reverse('projetos:detalhe', args=[self.projeto.pk])).context['entregas'])
        self.assertEqual(entregas[0].total_horas, Decimal('3.5'))

    def test_excluir_fase_preserva_horas(self):
        l = LancamentoHoras.objects.create(projeto=self.projeto, usuario=self.ana, data=self.hoje,
                                           horas=Decimal('2'), entrega=self.fase)
        self.fase.delete()
        l.refresh_from_db()
        self.assertIsNone(l.entrega)
        self.projeto.refresh_from_db()
        self.assertEqual(self.projeto.horas_consumidas, Decimal('2'))

    def test_clean_do_modelo_rejeita_fase_de_outro_projeto(self):
        from django.core.exceptions import ValidationError
        l = LancamentoHoras(projeto=self.projeto, usuario=self.ana, data=self.hoje,
                            horas=Decimal('1'), entrega=self.fase_alheia)
        with self.assertRaises(ValidationError):
            l.full_clean()
