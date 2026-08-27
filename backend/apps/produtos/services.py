from django.core.exceptions import ValidationError

from apps.audit.services import AuditoriaService

from .repositories import ProdutoRepository


class ProdutoService:
    def __init__(self, repository: ProdutoRepository = None, auditoria: AuditoriaService = None):
        self.repository = repository or ProdutoRepository()
        self.auditoria = auditoria or AuditoriaService()

    def listar(self):
        return self.repository.listar()

    def obter_por_id(self, produto_id):
        return self.repository.obter_por_id(produto_id)

    def criar_produto(self, *, criado_por, **dados):
        if self.repository.obter_por_codigo_interno(dados.get("codigo_interno")):
            raise ValidationError("Ja existe um produto com este codigo interno.")

        produto = self.repository.criar(**dados)

        self.auditoria.registrar(
            usuario=criado_por,
            acao="CRIAR_PRODUTO",
            modulo="Cadastro de Produtos",
            objeto=str(produto),
            dados_novos={"codigo_interno": produto.codigo_interno, "nome": produto.nome},
        )
        return produto

    def atualizar_produto(self, *, produto, atualizado_por, **dados):
        dados_anteriores = {
            "valor_compra": str(produto.valor_compra),
            "estoque_minimo": str(produto.estoque_minimo),
            "estoque_maximo": str(produto.estoque_maximo),
        }
        produto = self.repository.atualizar(produto, **dados)

        self.auditoria.registrar(
            usuario=atualizado_por,
            acao="ATUALIZAR_PRODUTO",
            modulo="Cadastro de Produtos",
            objeto=str(produto),
            dados_anteriores=dados_anteriores,
        )
        return produto

    def desativar_produto(self, *, produto, executor):
        produto.deletar()
        self.auditoria.registrar(
            usuario=executor,
            acao="DESATIVAR_PRODUTO",
            modulo="Cadastro de Produtos",
            objeto=str(produto),
        )
        return produto
