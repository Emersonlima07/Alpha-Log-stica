from django.core.exceptions import ValidationError

from apps.audit.services import AuditoriaService

from .repositories import FornecedorRepository


class FornecedorService:
    def __init__(self, repository: FornecedorRepository = None, auditoria: AuditoriaService = None):
        self.repository = repository or FornecedorRepository()
        self.auditoria = auditoria or AuditoriaService()

    def listar(self):
        return self.repository.listar()

    def criar_fornecedor(self, *, criado_por, **dados):
        if self.repository.obter_por_cnpj(dados.get("cnpj")):
            raise ValidationError("Ja existe um fornecedor cadastrado com este CNPJ.")
        fornecedor = self.repository.criar(**dados)
        self.auditoria.registrar(
            usuario=criado_por, acao="CRIAR_FORNECEDOR", modulo="Compras", objeto=str(fornecedor),
        )
        return fornecedor

    def atualizar_fornecedor(self, *, fornecedor, atualizado_por, **dados):
        fornecedor = self.repository.atualizar(fornecedor, **dados)
        self.auditoria.registrar(usuario=atualizado_por, acao="ATUALIZAR_FORNECEDOR", modulo="Compras", objeto=str(fornecedor))
        return fornecedor

    def avaliar_fornecedor(self, *, fornecedor, avaliador, pontualidade=None, qualidade=None):
        """Avaliacao manual (0 a 5). O Modulo 13 vai automatizar isso a
        partir do historico real de recebimentos no futuro."""
        if pontualidade is not None:
            fornecedor.avaliacao_pontualidade = pontualidade
        if qualidade is not None:
            fornecedor.avaliacao_qualidade = qualidade
        fornecedor.save(update_fields=["avaliacao_pontualidade", "avaliacao_qualidade"])
        self.auditoria.registrar(usuario=avaliador, acao="AVALIAR_FORNECEDOR", modulo="Compras", objeto=str(fornecedor))
        return fornecedor

    def desativar_fornecedor(self, *, fornecedor, executor):
        fornecedor.deletar()
        self.auditoria.registrar(usuario=executor, acao="DESATIVAR_FORNECEDOR", modulo="Compras", objeto=str(fornecedor))
        return fornecedor
