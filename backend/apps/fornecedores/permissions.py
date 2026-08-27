from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Perfil


class PodeGerenciarFornecedores(BasePermission):
    """Cadastro de fornecedores (Modulo 16: Comprador cadastra fornecedores)."""

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil in (Perfil.COMPRADOR, Perfil.ADMINISTRADOR, Perfil.SUPERVISOR, Perfil.DIRETORIA)
