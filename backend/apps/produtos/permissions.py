from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Perfil


class PodeGerenciarProdutos(BasePermission):
    """
    Qualquer usuario autenticado pode CONSULTAR produtos (Operador precisa
    para movimentar estoque, Comprador precisa para comprar, etc).
    Apenas Administrador, Supervisor e Diretoria podem CRIAR/EDITAR/EXCLUIR
    o cadastro em si -- e dado mestre, alterado com menos frequencia.
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil in (
            Perfil.ADMINISTRADOR,
            Perfil.SUPERVISOR,
            Perfil.DIRETORIA,
        )
