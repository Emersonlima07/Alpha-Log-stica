from django.core.exceptions import ValidationError

from apps.audit.services import AuditoriaService

from .repositories import UserRepository


class UserService:
    def __init__(self, repository: UserRepository = None, auditoria: AuditoriaService = None):
        self.repository = repository or UserRepository()
        self.auditoria = auditoria or AuditoriaService()

    def listar_por_empresa(self, empresa_id):
        return self.repository.listar_por_empresa(empresa_id)

    def criar_usuario(self, *, criado_por, password, **dados):
        if self.repository.obter_por_username(dados.get("username")):
            raise ValidationError("Ja existe um usuario com este nome de usuario.")

        usuario = self.repository.criar(password=password, **dados)

        self.auditoria.registrar(
            usuario=criado_por,
            acao="CRIAR_USUARIO",
            modulo="Administracao",
            objeto=str(usuario),
        )
        return usuario

    def desativar_usuario(self, *, usuario, executor):
        usuario.deletar()  # soft delete, herdado de BaseModel
        self.auditoria.registrar(
            usuario=executor,
            acao="DESATIVAR_USUARIO",
            modulo="Administracao",
            objeto=str(usuario),
        )
        return usuario
