from rest_framework import viewsets
from rest_framework.response import Response

from apps.users.models import Perfil
from apps.users.permissions import PerfilPermission

from .models import Empresa, Filial
from .serializers import EmpresaSerializer, FilialSerializer
from .services import EmpresaService, FilialService


class EmpresaViewSet(viewsets.ModelViewSet):
    queryset = Empresa.objects.all()
    serializer_class = EmpresaSerializer
    permission_classes = [PerfilPermission]
    perfis_permitidos = [Perfil.ADMINISTRADOR, Perfil.DIRETORIA]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = EmpresaService()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        empresa = self.service.criar_empresa(**serializer.validated_data)
        return Response(EmpresaSerializer(empresa).data, status=201)


class FilialViewSet(viewsets.ModelViewSet):
    queryset = Filial.objects.all()
    serializer_class = FilialSerializer
    permission_classes = [PerfilPermission]
    perfis_permitidos = [Perfil.ADMINISTRADOR, Perfil.DIRETORIA, Perfil.SUPERVISOR]
    filterset_fields = ["empresa"]
