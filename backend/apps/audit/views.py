from rest_framework import viewsets

from apps.users.models import Perfil
from apps.users.permissions import PerfilPermission

from .models import LogAuditoria
from .serializers import LogAuditoriaSerializer


class LogAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Somente Administrador e Diretoria podem consultar os logs de
    auditoria completos (Modulo 7 - Administracao).
    """

    queryset = LogAuditoria.objects.select_related("usuario").all()
    serializer_class = LogAuditoriaSerializer
    permission_classes = [PerfilPermission]
    perfis_permitidos = [Perfil.ADMINISTRADOR, Perfil.DIRETORIA]
    filterset_fields = ["modulo", "acao", "usuario"]
