from decimal import Decimal

from django.core.cache import cache
from django.urls import reverse
from rest_framework.test import APITestCase

from apps.compras.models import PedidoCompra, PedidoCompraItem, StatusPedido
from apps.core.models import Empresa, Filial
from apps.estoque.models import Lote
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto
from apps.recebimento.models import Recebimento, StatusRecebimento
from apps.recebimento.parsers import XmlNfeInvalidoError, parsear_xml_nfe
from apps.users.models import Perfil, User


XML_NFE_EXEMPLO = """<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe">
  <NFe>
    <infNFe Id="NFe35200714200166000187550010000000046550010204" versao="4.00">
      <ide><nNF>123</nNF></ide>
      <emit><CNPJ>14200166000187</CNPJ><xNome>Fornecedor XML Ltda</xNome></emit>
      <det nItem="1">
        <prod>
          <cProd>REC-001</cProd>
          <cEAN>7891000000001</cEAN>
          <xProd>Produto Recebido via XML</xProd>
          <qCom>15.0000</qCom>
          <vUnCom>9.90</vUnCom>
        </prod>
      </det>
    </infNFe>
  </NFe>
</nfeProc>
"""


class ParserXmlNfeTestCase(APITestCase):
    def test_parseia_xml_valido(self):
        dados = parsear_xml_nfe(XML_NFE_EXEMPLO)
        self.assertEqual(dados["numero_nf"], "123")
        self.assertEqual(len(dados["itens"]), 1)
        self.assertEqual(dados["itens"][0]["codigo_produto"], "REC-001")
        self.assertEqual(dados["itens"][0]["quantidade"], Decimal("15.0000"))

    def test_rejeita_xml_invalido(self):
        with self.assertRaises(XmlNfeInvalidoError):
            parsear_xml_nfe("<no><es>nfe</es></no>")

    def test_rejeita_texto_que_nao_e_xml(self):
        with self.assertRaises(XmlNfeInvalidoError):
            parsear_xml_nfe("isso definitivamente nao e um xml")


class RecebimentoFluxoTestCase(APITestCase):
    def setUp(self):
        cache.clear()
        self.empresa = Empresa.objects.create(razao_social="Empresa Recebimento", cnpj="55.555.555/0001-55")
        self.filial = Filial.objects.create(empresa=self.empresa, codigo="A", nome="Filial A")

        self.operador = User.objects.create_user(
            username="operador_receb", password="SenhaForte123", perfil=Perfil.OPERADOR_LOGISTICO, empresa=self.empresa,
        )
        self.supervisor = User.objects.create_user(
            username="supervisor_receb", password="SenhaForte123", perfil=Perfil.SUPERVISOR, empresa=self.empresa,
        )

        self.produto = Produto.objects.create(codigo_interno="REC-001", nome="Produto Recebido", unidade_medida="UN")
        self.fornecedor = Fornecedor.objects.create(razao_social="Fornecedor Receb Ltda", cnpj="66.666.666/0001-66")

        self.pedido = PedidoCompra.objects.create(
            numero="PC-000001", fornecedor=self.fornecedor, filial=self.filial, status=StatusPedido.ENVIADO,
        )
        self.pedido_item = PedidoCompraItem.objects.create(
            pedido=self.pedido, produto=self.produto, quantidade=Decimal("20"), valor_unitario=Decimal("5.00"),
        )

    def _login(self, username, password="SenhaForte123"):
        resp = self.client.post(reverse("login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_iniciar_recebimento_pre_preenche_itens_pendentes(self):
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id, "numero_nf": "999"})
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(len(resp.data["itens"]), 1)
        self.assertEqual(resp.data["itens"][0]["quantidade_nf"], "20.000")

    def test_conferir_item_detecta_divergencia(self):
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id})
        item_id = resp.data["itens"][0]["id"]

        resp = self.client.post(f"/api/recebimento/itens/{item_id}/conferir/", {"quantidade_conferida": "18", "numero_lote": "L1"})
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertTrue(resp.data["tem_divergencia"])  # 18 conferido != 20 da nota

    def test_operador_nao_pode_aprovar_recebimento(self):
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id})
        recebimento_id = resp.data["id"]
        resp = self.client.post(f"/api/recebimento/{recebimento_id}/aprovar/")
        self.assertEqual(resp.status_code, 403)

    def test_aprovacao_gera_entrada_real_no_estoque(self):
        """O teste mais importante do modulo: aprovar o recebimento tem
        que criar um MovimentoEstoque de ENTRADA de verdade."""
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id, "numero_nf": "999"})
        recebimento_id = resp.data["id"]
        item_id = resp.data["itens"][0]["id"]

        self.client.post(
            f"/api/recebimento/itens/{item_id}/conferir/",
            {"quantidade_conferida": "20", "numero_lote": "LOTE-A", "data_validade": "2027-01-01"},
        )

        self._login("supervisor_receb")
        resp = self.client.post(f"/api/recebimento/{recebimento_id}/aprovar/")
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertEqual(resp.data["status"], StatusRecebimento.APROVADO)

        # Confirma que o estoque de verdade recebeu a entrada
        lote = Lote.objects.get(produto=self.produto, filial=self.filial, numero_lote="LOTE-A")
        self.assertEqual(lote.quantidade_atual, Decimal("20.000"))

        # Confirma que o item do pedido foi atualizado e o pedido virou RECEBIDO
        self.pedido_item.refresh_from_db()
        self.assertEqual(self.pedido_item.quantidade_recebida, Decimal("20.000"))
        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, StatusPedido.RECEBIDO)

    def test_aprovacao_parcial_marca_pedido_como_parcialmente_recebido(self):
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id})
        recebimento_id = resp.data["id"]
        item_id = resp.data["itens"][0]["id"]
        self.client.post(f"/api/recebimento/itens/{item_id}/conferir/", {"quantidade_conferida": "10"})

        self._login("supervisor_receb")
        self.client.post(f"/api/recebimento/{recebimento_id}/aprovar/")

        self.pedido.refresh_from_db()
        self.assertEqual(self.pedido.status, StatusPedido.PARCIALMENTE_RECEBIDO)

    def test_rejeitar_recebimento_nao_mexe_no_estoque(self):
        self._login("operador_receb")
        resp = self.client.post("/api/recebimento/iniciar/", {"pedido_compra": self.pedido.id})
        recebimento_id = resp.data["id"]
        item_id = resp.data["itens"][0]["id"]
        self.client.post(f"/api/recebimento/itens/{item_id}/conferir/", {"quantidade_conferida": "20"})

        self._login("supervisor_receb")
        resp = self.client.post(f"/api/recebimento/{recebimento_id}/rejeitar/", {"motivo": "Produto avariado"})
        self.assertEqual(resp.status_code, 200, resp.data)
        self.assertFalse(Lote.objects.filter(produto=self.produto, filial=self.filial).exists())

    def test_importar_xml_cria_recebimento_com_itens(self):
        self._login("operador_receb")
        resp = self.client.post(
            "/api/recebimento/importar-xml/",
            {"pedido_compra": self.pedido.id, "xml_content": XML_NFE_EXEMPLO},
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(resp.data["numero_nf"], "123")
        self.assertEqual(len(resp.data["itens"]), 1)
        self.assertEqual(resp.data["itens"][0]["quantidade_nf"], "15.000")
