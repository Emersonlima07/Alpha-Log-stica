from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.compras.models import PedidoCompra, SolicitacaoCompra, StatusSolicitacao
from apps.core.models import Empresa, Filial
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.users.models import Perfil, User


class ComprasFluxoTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.empresa = Empresa.objects.create(razao_social="Empresa Compras", cnpj="44.444.444/0001-44")
        self.filial = Filial.objects.create(empresa=self.empresa, codigo="A", nome="Filial A")

        self.comprador = User.objects.create_user(
            username="comprador", password="SenhaForte123", perfil=Perfil.COMPRADOR, empresa=self.empresa,
        )
        self.supervisor = User.objects.create_user(
            username="supervisor_compras", password="SenhaForte123", perfil=Perfil.SUPERVISOR, empresa=self.empresa,
        )
        self.operador = User.objects.create_user(
            username="operador_compras", password="SenhaForte123", perfil=Perfil.OPERADOR_LOGISTICO, empresa=self.empresa,
        )

        self.produto = Produto.objects.create(codigo_interno="CMP-001", nome="Parafuso", unidade_medida="CX")
        self.fornecedor_a = Fornecedor.objects.create(razao_social="Fornecedor A Ltda", cnpj="11.111.111/0001-11")
        self.fornecedor_b = Fornecedor.objects.create(razao_social="Fornecedor B Ltda", cnpj="22.222.222/0001-22")

    def _login(self, username, password="SenhaForte123"):
        resp = self.client.post(reverse("login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_operador_nao_pode_solicitar_compra(self):
        self._login("operador_compras")
        resp = self.client.post(
            "/api/compras/solicitacoes/nova/",
            {"produto": self.produto.id, "filial": self.filial.id, "quantidade_solicitada": "50"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_fluxo_completo_ate_gerar_pedido(self):
        self._login("comprador")

        # 1. Solicitacao
        resp = self.client.post(
            "/api/compras/solicitacoes/nova/",
            {"produto": self.produto.id, "filial": self.filial.id, "quantidade_solicitada": "100", "motivo": "Estoque baixo"},
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        solicitacao_id = resp.data["id"]
        self.assertEqual(resp.data["status"], StatusSolicitacao.PENDENTE)

        # 2. Duas cotacoes
        resp = self.client.post(
            f"/api/compras/solicitacoes/{solicitacao_id}/cotacoes/",
            {"fornecedor": self.fornecedor_a.id, "valor_unitario": "12.50", "prazo_entrega_dias": 5},
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        cotacao_a_id = resp.data["id"]

        resp = self.client.post(
            f"/api/compras/solicitacoes/{solicitacao_id}/cotacoes/",
            {"fornecedor": self.fornecedor_b.id, "valor_unitario": "10.00", "prazo_entrega_dias": 10},
        )
        self.assertEqual(resp.status_code, 201, resp.data)

        # status deve ter virado EM_COTACAO
        solicitacao = SolicitacaoCompra.objects.get(id=solicitacao_id)
        self.assertEqual(solicitacao.status, StatusSolicitacao.EM_COTACAO)

        # 3. Selecionar a cotacao mais barata (fornecedor A, so pra testar o fluxo)
        resp = self.client.post(f"/api/compras/cotacoes/{cotacao_a_id}/selecionar/")
        self.assertEqual(resp.status_code, 200, resp.data)

        # 4. Comprador nao pode aprovar (so Supervisor+)
        resp = self.client.post(f"/api/compras/solicitacoes/{solicitacao_id}/aprovar/")
        self.assertEqual(resp.status_code, 403)

        # 5. Supervisor aprova -> gera pedido automaticamente
        self._login("supervisor_compras")
        resp = self.client.post(f"/api/compras/solicitacoes/{solicitacao_id}/aprovar/")
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["fornecedor"], self.fornecedor_a.id)
        self.assertEqual(len(resp.data["itens"]), 1)
        self.assertEqual(resp.data["itens"][0]["quantidade"], "100.000")

        pedido = PedidoCompra.objects.get(numero=resp.data["numero"])
        self.assertEqual(pedido.valor_total, 1250)  # 12.50 * 100

        solicitacao.refresh_from_db()
        self.assertEqual(solicitacao.status, StatusSolicitacao.CONVERTIDA)

    def test_nao_aprova_sem_cotacao_selecionada(self):
        self._login("comprador")
        resp = self.client.post(
            "/api/compras/solicitacoes/nova/",
            {"produto": self.produto.id, "filial": self.filial.id, "quantidade_solicitada": "10"},
        )
        solicitacao_id = resp.data["id"]

        self._login("supervisor_compras")
        resp = self.client.post(f"/api/compras/solicitacoes/{solicitacao_id}/aprovar/")
        self.assertEqual(resp.status_code, 400)

    def test_rejeitar_solicitacao_exige_motivo(self):
        self._login("comprador")
        resp = self.client.post(
            "/api/compras/solicitacoes/nova/",
            {"produto": self.produto.id, "filial": self.filial.id, "quantidade_solicitada": "10"},
        )
        solicitacao_id = resp.data["id"]

        self._login("supervisor_compras")
        resp = self.client.post(f"/api/compras/solicitacoes/{solicitacao_id}/rejeitar/", {"motivo": ""})
        self.assertEqual(resp.status_code, 400)

        resp = self.client.post(f"/api/compras/solicitacoes/{solicitacao_id}/rejeitar/", {"motivo": "Preco fora do orcamento"})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["status"], StatusSolicitacao.REJEITADA)
