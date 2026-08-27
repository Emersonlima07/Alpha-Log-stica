from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from ..models import Perfil
from ..permissions import IsAdministradorOuDiretoria
from ..serializers import CustomTokenObtainPairSerializer, UserCreateSerializer, UserSerializer
from ..services import UserService


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/  {username, password} -> access + refresh token"""

    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [AllowAny]


class RefreshView(TokenRefreshView):
    permission_classes = [AllowAny]


class MeView(APIView):
    """GET /api/auth/me/ -> dados do usuario autenticado (para o frontend montar o app)."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class UserViewSet(viewsets.ModelViewSet):
    """
    CRUD de usuarios. Restrito a Administrador/Diretoria (Modulo 7).
    A criacao/edicao usa o UserService, nunca o ORM direto na view.
    """

    serializer_class = UserSerializer
    permission_classes = [IsAdministradorOuDiretoria]
    filterset_fields = ["perfil", "empresa", "filial", "ativo"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = UserService()

    def get_queryset(self):
        empresa_id = self.request.user.empresa_id
        return self.service.listar_por_empresa(empresa_id)

    def create(self, request, *args, **kwargs):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = dict(serializer.validated_data)
        password = dados.pop("password")
        usuario = self.service.criar_usuario(
            criado_por=request.user, password=password, **dados
        )
        return Response(UserSerializer(usuario).data, status=201)

    def destroy(self, request, *args, **kwargs):
        usuario = self.get_object()
        self.service.desativar_usuario(usuario=usuario, executor=request.user)
        return Response(status=204)


# Perfis disponiveis, para o frontend popular selects sem hardcode.
class PerfisDisponiveisView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response([{"value": v, "label": l} for v, l in Perfil.choices])
