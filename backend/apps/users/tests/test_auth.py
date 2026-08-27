from django.urls import reverse
from rest_framework.test import APITestCase

from apps.core.models import Empresa
from apps.users.models import Perfil, User


class AutenticacaoTestCase(APITestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(razao_social="Empresa Teste", cnpj="11.111.111/0001-11")
        self.admin = User.objects.create_user(
            username="admin_teste",
            password="SenhaForte123",
            perfil=Perfil.ADMINISTRADOR,
            empresa=self.empresa,
        )
        self.operador = User.objects.create_user(
            username="operador_teste",
            password="SenhaForte123",
            perfil=Perfil.OPERADOR_LOGISTICO,
            empresa=self.empresa,
        )

    def test_login_com_credenciais_validas_retorna_tokens(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin_teste", "password": "SenhaForte123"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_com_credenciais_invalidas_falha(self):
        response = self.client.post(
            reverse("login"),
            {"username": "admin_teste", "password": "senha_errada"},
        )
        self.assertEqual(response.status_code, 401)

    def test_operador_nao_pode_listar_usuarios(self):
        login = self.client.post(
            reverse("login"),
            {"username": "operador_teste", "password": "SenhaForte123"},
        )
        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/usuarios/")
        self.assertEqual(response.status_code, 403)

    def test_admin_pode_listar_usuarios(self):
        login = self.client.post(
            reverse("login"),
            {"username": "admin_teste", "password": "SenhaForte123"},
        )
        token = login.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        response = self.client.get("/api/auth/usuarios/")
        self.assertEqual(response.status_code, 200)

    def test_desativar_usuario_e_soft_delete(self):
        self.operador.deletar()
        self.assertFalse(User.objects.filter(id=self.operador.id).exists())  # manager padrao filtra ativo=True
        self.assertTrue(User.todos_objects.filter(id=self.operador.id).exists())
