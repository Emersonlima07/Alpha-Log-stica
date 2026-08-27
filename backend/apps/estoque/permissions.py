from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Perfil


class PodeMovimentarEstoque(BasePermission):
    """Entrada, saida, transferencia e baixa: Operador de Logistica pra cima."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil in (
            Perfil.OPERADOR_LOGISTICO,
            Perfil.SUPERVISOR,
            Perfil.ADMINISTRADOR,
            Perfil.DIRETORIA,
        )


class PodeAjustarEstoque(BasePermission):
    """
    Ajuste de estoque (correcao apos inventario) exige liberacao de
    Supervisor pra cima -- Operador nao pode ajustar sozinho, conforme
    Modulo 16 ("Supervisor: liberar ajustes").
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil in (Perfil.SUPERVISOR, Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
        )
