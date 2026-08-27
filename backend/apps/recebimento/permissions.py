from rest_framework.permissions import SAFE_METHODS, BasePermission

from apps.users.models import Perfil


class PodeReceber(BasePermission):
    """
    Iniciar recebimento, importar XML e conferir itens: Operador de
    Logistica pra cima (Modulo 16: 'Recebimento de notas fiscais',
    'Conferencia fisica das mercadorias', 'Receber mercadorias').
    """

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.perfil in (Perfil.OPERADOR_LOGISTICO, Perfil.SUPERVISOR, Perfil.ADMINISTRADOR, Perfil.DIRETORIA)


class PodeAprovarRecebimento(BasePermission):
    """
    Aprovar ou rejeitar o recebimento: Supervisor pra cima, porque essa
    acao e irreversivel -- ela gera entrada de verdade no estoque.
    """

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated
            and request.user.perfil in (Perfil.SUPERVISOR, Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
        )
