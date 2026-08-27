from rest_framework.permissions import BasePermission

from .models import Perfil


class PerfilPermission(BasePermission):
    """
    Permissao generica parametrizavel por lista de perfis permitidos.
    Use via `perfis_permitidos` na view, ou pelas subclasses prontas abaixo.

    Exemplo de uso direto numa view:
        permission_classes = [PerfilPermission]
        perfis_permitidos = [Perfil.ADMINISTRADOR, Perfil.DIRETORIA]
    """

    message = "Seu perfil nao tem permissao para executar esta acao."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        perfis_permitidos = getattr(view, "perfis_permitidos", None)
        if not perfis_permitidos:
            # Se a view nao declarar perfis explicitamente, nega por padrao.
            # Isso forca toda nova view de qualquer modulo a declarar
            # explicitamente quem pode acessa-la (fail-safe).
            return False
        return request.user.perfil in perfis_permitidos


class IsAdministrador(PerfilPermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil == Perfil.ADMINISTRADOR
        )


class IsAdministradorOuDiretoria(PerfilPermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil in (Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
        )


class IsSupervisorOuAcima(PerfilPermission):
    """Supervisor, Administrador ou Diretoria."""

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil
            in (Perfil.SUPERVISOR, Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
        )


class IsComprador(PerfilPermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil in (Perfil.COMPRADOR, Perfil.ADMINISTRADOR)
        )


class IsOperadorLogistico(PerfilPermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.perfil
            in (Perfil.OPERADOR_LOGISTICO, Perfil.SUPERVISOR, Perfil.ADMINISTRADOR)
        )
