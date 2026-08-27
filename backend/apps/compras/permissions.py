from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Perfil


class PodeSolicitarCompra(BasePermission):
    """Criar solicitacoes e cotacoes: Comprador pra cima (Modulo 16: 'Comprador solicita compras')."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil in (Perfil.COMPRADOR, Perfil.ADMINISTRADOR, Perfil.SUPERVISOR, Perfil.DIRETORIA)


class PodeAprovarCompra(BasePermission):
    """Aprovar/rejeitar solicitacoes: Supervisor pra cima (Modulo 16: 'Supervisor aprova compras')."""

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.perfil in (Perfil.SUPERVISOR, Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
        )
