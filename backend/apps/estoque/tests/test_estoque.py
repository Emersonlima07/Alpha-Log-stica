from decimal import Decimal

from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Empresa, Filial
from apps.estoque.models import Lote, MovimentoEstoque
from apps.produtos.models import Produto
from apps.users.models import Perfil, User


class EstoqueAPITestCase(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(razao_social="Empresa Estoque", cnpj="33.333.333/0001-33")
        self.filial_a = Filial.objects.create(empresa=self.empresa, codigo="A", nome="Filial A")
        self.filial_b = Filial.objects.create(empresa=self.empresa, codigo="B", nome="Filial B")

        self.operador = User.objects.create_user(
            username="operador_estoque", password="SenhaForte123",
            perfil=Perfil.OPERADOR_LOGISTICO, empresa=self.empresa,
        )
        self.supervisor = User.objects.create_user(
            username="supervisor_estoque", password="SenhaForte123",
            perfil=Perfil.SUPERVISOR, empresa=self.empresa,
        )

        self.produto = Produto.objects.create(
            codigo_interno="EST-001", nome="Caixa de Parafusos", unidade_medida="CX",
        )

    def _login(self, username, password="SenhaForte123"):
        resp = self.client.post(reverse("login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_entrada_aumenta_saldo_do_lote(self):
        self._login("operador_estoque")
        resp = self.client.post(
            "/api/estoque/entrada/",
            {
                "produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10",
                "numero_lote": "L1", "valor_unitario": "5.50",
            },
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        lote = Lote.objects.get(produto=self.produto, filial=self.filial_a, numero_lote="L1")
        self.assertEqual(lote.quantidade_atual, Decimal("10.000"))

    def test_saida_diminui_saldo_do_lote(self):
        self._login("operador_estoque")
        self.client.post(
            "/api/estoque/entrada/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10", "numero_lote": "L1"},
        )
        resp = self.client.post(
            "/api/estoque/saida/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "4", "numero_lote": "L1"},
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        lote = Lote.objects.get(produto=self.produto, filial=self.filial_a, numero_lote="L1")
        self.assertEqual(lote.quantidade_atual, Decimal("6.000"))

    def test_saida_maior_que_saldo_e_bloqueada(self):
        """O teste mais importante do modulo: nunca permitir estoque negativo."""
        self._login("operador_estoque")
        self.client.post(
            "/api/estoque/entrada/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "5", "numero_lote": "L1"},
        )
        resp = self.client.post(
            "/api/estoque/saida/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "999", "numero_lote": "L1"},
        )
        self.assertEqual(resp.status_code, 400)
        lote = Lote.objects.get(produto=self.produto, filial=self.filial_a, numero_lote="L1")
        self.assertEqual(lote.quantidade_atual, Decimal("5.000"))  # saldo intacto, nao mexeu

    def test_saida_sem_lote_existente_e_bloqueada(self):
        self._login("operador_estoque")
        resp = self.client.post(
            "/api/estoque/saida/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "1", "numero_lote": "INEXISTENTE"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_transferencia_move_saldo_entre_filiais(self):
        self._login("operador_estoque")
        self.client.post(
            "/api/estoque/entrada/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10", "numero_lote": "L1"},
        )
        resp = self.client.post(
            "/api/estoque/transferencia/",
            {
                "produto": self.produto.id, "filial_origem": self.filial_a.id,
                "filial_destino": self.filial_b.id, "quantidade": "3", "numero_lote": "L1",
            },
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        origem = Lote.objects.get(produto=self.produto, filial=self.filial_a, numero_lote="L1")
        destino = Lote.objects.get(produto=self.produto, filial=self.filial_b, numero_lote="L1")
        self.assertEqual(origem.quantidade_atual, Decimal("7.000"))
        self.assertEqual(destino.quantidade_atual, Decimal("3.000"))

    def test_operador_nao_pode_ajustar_estoque(self):
        self._login("operador_estoque")
        resp = self.client.post(
            "/api/estoque/ajuste/",
            {
                "produto": self.produto.id, "filial": self.filial_a.id,
                "nova_quantidade": "50", "motivo": "Contagem de inventario",
            },
        )
        self.assertEqual(resp.status_code, 403)

    def test_supervisor_pode_ajustar_estoque(self):
        self._login("supervisor_estoque")
        resp = self.client.post(
            "/api/estoque/ajuste/",
            {
                "produto": self.produto.id, "filial": self.filial_a.id,
                "nova_quantidade": "50", "motivo": "Contagem de inventario",
            },
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        lote = Lote.objects.get(produto=self.produto, filial=self.filial_a, numero_lote="UNICO")
        self.assertEqual(lote.quantidade_atual, Decimal("50.000"))

    def test_ajuste_sem_motivo_e_rejeitado(self):
        self._login("supervisor_estoque")
        resp = self.client.post(
            "/api/estoque/ajuste/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "nova_quantidade": "50", "motivo": ""},
        )
        self.assertEqual(resp.status_code, 400)

    def test_entrada_gera_log_de_auditoria(self):
        from apps.audit.models import LogAuditoria

        self._login("operador_estoque")
        self.client.post(
            "/api/estoque/entrada/",
            {"produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10", "numero_lote": "L1"},
        )
        self.assertTrue(
            LogAuditoria.objects.filter(modulo="Controle de Estoque", acao="MOVIMENTO_ENTRADA").exists()
        )

    def test_valor_medio_recalculado_apos_entrada(self):
        self._login("operador_estoque")
        self.client.post(
            "/api/estoque/entrada/",
            {
                "produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10",
                "numero_lote": "L1", "valor_unitario": "10.00",
            },
        )
        self.client.post(
            "/api/estoque/entrada/",
            {
                "produto": self.produto.id, "filial": self.filial_a.id, "quantidade": "10",
                "numero_lote": "L2", "valor_unitario": "20.00",
            },
        )
        self.produto.refresh_from_db()
        # (10*10 + 10*20) / 20 = 15.00
        self.assertEqual(self.produto.valor_medio, Decimal("15.00"))
