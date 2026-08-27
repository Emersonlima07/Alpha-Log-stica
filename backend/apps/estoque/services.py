from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import AuditoriaService

from .models import MovimentoEstoque, TipoMovimento
from .repositories import LoteRepository, MovimentoEstoqueRepository


class EstoqueService:
    def __init__(
        self,
        lote_repository: LoteRepository = None,
        movimento_repository: MovimentoEstoqueRepository = None,
        auditoria: AuditoriaService = None,
    ):
        self.lotes = lote_repository or LoteRepository()
        self.movimentos = movimento_repository or MovimentoEstoqueRepository()
        self.auditoria = auditoria or AuditoriaService()

    # ------------------------------------------------------------------
    # Entrada
    # ------------------------------------------------------------------
    @transaction.atomic
    def registrar_entrada(
        self, *, produto, filial, quantidade, usuario, numero_lote=None,
        data_validade=None, valor_unitario=None, motivo=""
    ):
        quantidade = Decimal(quantidade)
        if quantidade <= 0:
            raise ValidationError("Quantidade de entrada deve ser maior que zero.")

        lote = self.lotes.obter_ou_criar(
            produto=produto,
            filial=filial,
            numero_lote=numero_lote,
            data_validade=data_validade,
            valor_unitario=valor_unitario,
        )
        lote.quantidade_atual += quantidade
        if valor_unitario is not None:
            lote.valor_unitario = valor_unitario
        self.lotes.salvar(lote)

        self._recalcular_valor_medio(produto)

        movimento = self.movimentos.criar(
            tipo=TipoMovimento.ENTRADA,
            produto=produto,
            lote=lote,
            quantidade=quantidade,
            filial_destino=filial,
            motivo=motivo,
            usuario=usuario,
        )
        self._auditar(movimento, usuario)
        return movimento

    # ------------------------------------------------------------------
    # Saida
    # ------------------------------------------------------------------
    @transaction.atomic
    def registrar_saida(self, *, produto, filial, quantidade, usuario, numero_lote=None, motivo=""):
        return self._sair(
            tipo=TipoMovimento.SAIDA, produto=produto, filial=filial, quantidade=quantidade,
            usuario=usuario, numero_lote=numero_lote, motivo=motivo,
        )

    @transaction.atomic
    def dar_baixa(self, *, produto, filial, quantidade, usuario, numero_lote=None, motivo=""):
        if not motivo:
            raise ValidationError("Toda baixa de estoque precisa de um motivo (perda, avaria, vencimento etc).")
        return self._sair(
            tipo=TipoMovimento.BAIXA, produto=produto, filial=filial, quantidade=quantidade,
            usuario=usuario, numero_lote=numero_lote, motivo=motivo,
        )

    def _sair(self, *, tipo, produto, filial, quantidade, usuario, numero_lote, motivo):
        quantidade = Decimal(quantidade)
        if quantidade <= 0:
            raise ValidationError("Quantidade de saida deve ser maior que zero.")

        lote = self.lotes.obter(produto=produto, filial=filial, numero_lote=numero_lote)
        if lote is None or lote.quantidade_atual < quantidade:
            saldo = lote.quantidade_atual if lote else Decimal("0")
            raise ValidationError(
                f"Estoque insuficiente para {produto.codigo_interno} na filial {filial.codigo}: "
                f"saldo atual e {saldo}, solicitado {quantidade}. "
                "A operacao foi bloqueada para nao permitir estoque negativo."
            )

        lote.quantidade_atual -= quantidade
        self.lotes.salvar(lote)

        movimento = self.movimentos.criar(
            tipo=tipo,
            produto=produto,
            lote=lote,
            quantidade=quantidade,
            filial_origem=filial,
            motivo=motivo,
            usuario=usuario,
        )
        self._auditar(movimento, usuario)
        return movimento

    # ------------------------------------------------------------------
    # Transferencia entre filiais
    # ------------------------------------------------------------------
    @transaction.atomic
    def transferir(
        self, *, produto, filial_origem, filial_destino, quantidade, usuario, numero_lote=None, motivo=""
    ):
        quantidade = Decimal(quantidade)
        if quantidade <= 0:
            raise ValidationError("Quantidade de transferencia deve ser maior que zero.")
        if filial_origem.id == filial_destino.id:
            raise ValidationError("Filial de origem e destino nao podem ser a mesma.")

        lote_origem = self.lotes.obter(produto=produto, filial=filial_origem, numero_lote=numero_lote)
        if lote_origem is None or lote_origem.quantidade_atual < quantidade:
            saldo = lote_origem.quantidade_atual if lote_origem else Decimal("0")
            raise ValidationError(
                f"Estoque insuficiente para transferir: saldo atual e {saldo}, solicitado {quantidade}."
            )

        lote_origem.quantidade_atual -= quantidade
        self.lotes.salvar(lote_origem)

        lote_destino = self.lotes.obter_ou_criar(
            produto=produto,
            filial=filial_destino,
            numero_lote=numero_lote,
            data_validade=lote_origem.data_validade,
            valor_unitario=lote_origem.valor_unitario,
        )
        lote_destino.quantidade_atual += quantidade
        self.lotes.salvar(lote_destino)

        movimento = self.movimentos.criar(
            tipo=TipoMovimento.TRANSFERENCIA,
            produto=produto,
            lote=lote_origem,
            quantidade=quantidade,
            filial_origem=filial_origem,
            filial_destino=filial_destino,
            motivo=motivo,
            usuario=usuario,
        )
        self._auditar(movimento, usuario)
        return movimento

    # ------------------------------------------------------------------
    # Ajuste (correcao de inventario) -- Supervisor/Administrador/Diretoria
    # ------------------------------------------------------------------
    @transaction.atomic
    def ajustar(self, *, produto, filial, nova_quantidade, usuario, numero_lote=None, motivo=""):
        if not motivo:
            raise ValidationError("Todo ajuste de estoque precisa de um motivo (justificativa do inventario).")
        nova_quantidade = Decimal(nova_quantidade)
        if nova_quantidade < 0:
            raise ValidationError("A nova quantidade nao pode ser negativa.")

        lote = self.lotes.obter_ou_criar(produto=produto, filial=filial, numero_lote=numero_lote)
        delta = nova_quantidade - lote.quantidade_atual
        lote.quantidade_atual = nova_quantidade
        self.lotes.salvar(lote)

        movimento = self.movimentos.criar(
            tipo=TipoMovimento.AJUSTE,
            produto=produto,
            lote=lote,
            quantidade=delta,
            filial_origem=filial if delta < 0 else None,
            filial_destino=filial if delta >= 0 else None,
            motivo=motivo,
            usuario=usuario,
        )
        self._auditar(movimento, usuario)
        return movimento

    # ------------------------------------------------------------------
    # Consultas (Modulo 3: por lote, por validade; historico completo)
    # ------------------------------------------------------------------
    def consultar_lotes_por_produto(self, produto_id):
        return self.lotes.por_produto(produto_id)

    def consultar_por_validade(self, data_limite):
        return self.lotes.por_validade_ate(data_limite)

    def historico(self, *, produto_id=None, filial_id=None, tipo=None):
        return self.movimentos.historico(produto_id=produto_id, filial_id=filial_id, tipo=tipo)

    # ------------------------------------------------------------------
    # Internos
    # ------------------------------------------------------------------
    def _recalcular_valor_medio(self, produto):
        """Custo medio ponderado entre todos os lotes ativos do produto."""
        lotes = produto.lotes.filter(quantidade_atual__gt=0)
        quantidade_total = sum((l.quantidade_atual for l in lotes), Decimal("0"))
        if quantidade_total > 0:
            valor_total = sum((l.quantidade_atual * l.valor_unitario for l in lotes), Decimal("0"))
            produto.valor_medio = (valor_total / quantidade_total).quantize(Decimal("0.01"))
        produto.save(update_fields=["valor_medio"])

    def _auditar(self, movimento: MovimentoEstoque, usuario):
        self.auditoria.registrar(
            usuario=usuario,
            acao=f"MOVIMENTO_{movimento.tipo}",
            modulo="Controle de Estoque",
            objeto=str(movimento),
            dados_novos={
                "produto": movimento.produto.codigo_interno,
                "quantidade": str(movimento.quantidade),
                "lote": movimento.lote.numero_lote,
            },
        )
