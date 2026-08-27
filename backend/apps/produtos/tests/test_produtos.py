from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Empresa
from apps.produtos.models import Categoria, Fabricante, Produto
from apps.users.models import Perfil, User


class ProdutoAPITestCase(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(razao_social="Empresa Teste", cnpj="22.222.222/0001-22")
        self.admin = User.objects.create_user(
            username="admin_prod", password="SenhaForte123", perfil=Perfil.ADMINISTRADOR, empresa=self.empresa
        )
        self.operador = User.objects.create_user(
            username="operador_prod",
            password="SenhaForte123",
            perfil=Perfil.OPERADOR_LOGISTICO,
            empresa=self.empresa,
        )
        self.categoria = Categoria.objects.create(nome="Bebidas")
        self.fabricante = Fabricante.objects.create(nome="Fabricante XYZ")

    def _login(self, username, password="SenhaForte123"):
        resp = self.client.post(reverse("login"), {"username": username, "password": password})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {resp.data['access']}")

    def test_admin_pode_criar_produto(self):
        self._login("admin_prod")
        resp = self.client.post(
            "/api/produtos/produtos/",
            {
                "codigo_interno": "PRD-001",
                "nome": "Refrigerante 2L",
                "categoria": self.categoria.id,
                "fabricante": self.fabricante.id,
                "unidade_medida": "UN",
                "estoque_minimo": 10,
                "estoque_maximo": 100,
            },
        )
        self.assertEqual(resp.status_code, 201, resp.data)
        self.assertEqual(Produto.objects.count(), 1)

    def test_operador_nao_pode_criar_produto(self):
        self._login("operador_prod")
        resp = self.client.post(
            "/api/produtos/produtos/",
            {"codigo_interno": "PRD-002", "nome": "Produto X", "unidade_medida": "UN"},
        )
        self.assertEqual(resp.status_code, 403)

    def test_operador_pode_listar_produtos(self):
        Produto.objects.create(codigo_interno="PRD-003", nome="Produto Y", unidade_medida="UN")
        self._login("operador_prod")
        resp = self.client.get("/api/produtos/produtos/")
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(resp.data["count"], 1)

    def test_nao_permite_codigo_interno_duplicado(self):
        Produto.objects.create(codigo_interno="PRD-004", nome="Produto Z", unidade_medida="UN")
        self._login("admin_prod")
        resp = self.client.post(
            "/api/produtos/produtos/",
            {"codigo_interno": "PRD-004", "nome": "Outro nome", "unidade_medida": "UN"},
        )
        self.assertEqual(resp.status_code, 400)

    def test_estoque_maximo_menor_que_minimo_e_invalido(self):
        self._login("admin_prod")
        resp = self.client.post(
            "/api/produtos/produtos/",
            {
                "codigo_interno": "PRD-005",
                "nome": "Produto W",
                "unidade_medida": "UN",
                "estoque_minimo": 50,
                "estoque_maximo": 10,
            },
        )
        self.assertEqual(resp.status_code, 400)
