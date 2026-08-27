from .middleware import get_client_ip
from .models import LogAuditoria


class AuditoriaService:
    def registrar(
        self,
        *,
        usuario,
        acao,
        modulo,
        objeto="",
        dados_anteriores=None,
        dados_novos=None,
    ):
        return LogAuditoria.objects.create(
            usuario=usuario,
            acao=acao,
            modulo=modulo,
            objeto=objeto,
            dados_anteriores=dados_anteriores,
            dados_novos=dados_novos,
            ip=get_client_ip(),
        )

    def listar_por_modulo(self, modulo):
        return LogAuditoria.objects.filter(modulo=modulo)
