from decimal import Decimal

from django.core.exceptions import ValidationError
from django.db import transaction

from apps.audit.services import AuditoriaService

from .models import StatusPedido, StatusSolicitacao
from .repositories import (
    CotacaoRepository,
    PedidoCompraItemRepository,
    PedidoCompraRepository,
    SolicitacaoCompraRepository,
)


class ComprasService:
    def __init__(
        self,
        solicitacao_repository: SolicitacaoCompraRepository = None,
        cotacao_repository: CotacaoRepository = None,
        pedido_repository: PedidoCompraRepository = None,
        pedido_item_repository: PedidoCompraItemRepository = None,
        auditoria: AuditoriaService = None,
    ):
        self.solicitacoes = solicitacao_repository or SolicitacaoCompraRepository()
        self.cotacoes = cotacao_repository or CotacaoRepository()
        self.pedidos = pedido_repository or PedidoCompraRepository()
        self.itens_pedido = pedido_item_repository or PedidoCompraItemRepository()
        self.auditoria = auditoria or AuditoriaService()

    def listar_solicitacoes(self):
        return self.solicitacoes.listar()

    def listar_pedidos(self):
        return self.pedidos.listar()

    # ------------------------------------------------------------------
    # Solicitacao
    # ------------------------------------------------------------------
    def criar_solicitacao(self, *, produto, filial, quantidade_solicitada, solicitante, motivo=""):
        quantidade_solicitada = Decimal(str(quantidade_solicitada))
        if quantidade_solicitada <= 0:
            raise ValidationError("A quantidade solicitada deve ser maior que zero.")
        solicitacao = self.solicitacoes.criar(
            produto=produto, filial=filial, quantidade_solicitada=quantidade_solicitada,
            solicitante=solicitante, motivo=motivo,
        )
        self.auditoria.registrar(
            usuario=solicitante, acao="CRIAR_SOLICITACAO_COMPRA", modulo="Compras", objeto=str(solicitacao),
        )
        return solicitacao

    # ------------------------------------------------------------------
    # Cotacao
    # ------------------------------------------------------------------
    def adicionar_cotacao(self, *, solicitacao, fornecedor, valor_unitario, usuario, prazo_entrega_dias=0, condicoes_pagamento=""):
        if solicitacao.status not in (StatusSolicitacao.PENDENTE, StatusSolicitacao.EM_COTACAO):
            raise ValidationError("So e possivel cotar solicitacoes pendentes ou ja em cotacao.")
        valor_unitario = Decimal(str(valor_unitario))
        if valor_unitario <= 0:
            raise ValidationError("O valor unitario da cotacao deve ser maior que zero.")

        cotacao = self.cotacoes.criar(
            solicitacao=solicitacao, fornecedor=fornecedor, valor_unitario=valor_unitario,
            prazo_entrega_dias=prazo_entrega_dias, condicoes_pagamento=condicoes_pagamento,
        )
        if solicitacao.status == StatusSolicitacao.PENDENTE:
            self.solicitacoes.atualizar(solicitacao, status=StatusSolicitacao.EM_COTACAO)

        self.auditoria.registrar(
            usuario=usuario, acao="ADICIONAR_COTACAO", modulo="Compras", objeto=str(cotacao),
            dados_novos={"fornecedor": str(fornecedor), "valor_unitario": str(valor_unitario)},
        )
        return cotacao

    def selecionar_cotacao(self, *, cotacao, usuario):
        self.cotacoes.desmarcar_selecionadas(cotacao.solicitacao_id)
        cotacao.selecionada = True
        cotacao.save(update_fields=["selecionada"])
        self.auditoria.registrar(usuario=usuario, acao="SELECIONAR_COTACAO", modulo="Compras", objeto=str(cotacao))
        return cotacao

    # ------------------------------------------------------------------
    # Aprovacao -> gera Pedido de Compra automaticamente
    # ------------------------------------------------------------------
    @transaction.atomic
    def aprovar_solicitacao(self, *, solicitacao, aprovador, observacao=""):
        if solicitacao.status not in (StatusSolicitacao.PENDENTE, StatusSolicitacao.EM_COTACAO):
            raise ValidationError("Esta solicitacao ja foi processada (aprovada, rejeitada ou convertida).")

        cotacao_selecionada = solicitacao.cotacoes.filter(selecionada=True).first()
        if not cotacao_selecionada:
            raise ValidationError(
                "Nao e possivel aprovar sem uma cotacao selecionada. Adicione ao menos uma "
                "cotacao e marque-a como selecionada antes de aprovar."
            )

        self.solicitacoes.atualizar(
            solicitacao, status=StatusSolicitacao.APROVADA, aprovado_por=aprovador, observacao_aprovacao=observacao,
        )

        pedido = self.pedidos.criar(
            numero=self.pedidos.proximo_numero(),
            fornecedor=cotacao_selecionada.fornecedor,
            filial=solicitacao.filial,
            solicitacao_origem=solicitacao,
            criado_por=aprovador,
            valor_total=cotacao_selecionada.valor_unitario * solicitacao.quantidade_solicitada,
        )
        self.itens_pedido.criar(
            pedido=pedido, produto=solicitacao.produto, quantidade=solicitacao.quantidade_solicitada,
            valor_unitario=cotacao_selecionada.valor_unitario,
        )
        self.solicitacoes.atualizar(solicitacao, status=StatusSolicitacao.CONVERTIDA)

        self.auditoria.registrar(
            usuario=aprovador, acao="APROVAR_SOLICITACAO_COMPRA", modulo="Compras", objeto=str(solicitacao),
            dados_novos={"pedido_gerado": pedido.numero},
        )
        return pedido

    def rejeitar_solicitacao(self, *, solicitacao, aprovador, motivo):
        if not motivo:
            raise ValidationError("Informe o motivo da rejeicao.")
        if solicitacao.status not in (StatusSolicitacao.PENDENTE, StatusSolicitacao.EM_COTACAO):
            raise ValidationError("Esta solicitacao ja foi processada.")
        self.solicitacoes.atualizar(
            solicitacao, status=StatusSolicitacao.REJEITADA, aprovado_por=aprovador, observacao_aprovacao=motivo,
        )
        self.auditoria.registrar(usuario=aprovador, acao="REJEITAR_SOLICITACAO_COMPRA", modulo="Compras", objeto=str(solicitacao))
        return solicitacao

    # ------------------------------------------------------------------
    # Acompanhamento do pedido
    # ------------------------------------------------------------------
    def marcar_pedido_enviado(self, *, pedido, usuario):
        if pedido.status != StatusPedido.ABERTO:
            raise ValidationError("Apenas pedidos abertos podem ser marcados como enviados.")
        self.pedidos.atualizar(pedido, status=StatusPedido.ENVIADO)
        self.auditoria.registrar(usuario=usuario, acao="ENVIAR_PEDIDO_COMPRA", modulo="Compras", objeto=str(pedido))
        return pedido

    def cancelar_pedido(self, *, pedido, usuario, motivo):
        if pedido.status in (StatusPedido.RECEBIDO, StatusPedido.CANCELADO):
            raise ValidationError("Este pedido nao pode mais ser cancelado.")
        if not motivo:
            raise ValidationError("Informe o motivo do cancelamento.")
        self.pedidos.atualizar(pedido, status=StatusPedido.CANCELADO)
        self.auditoria.registrar(
            usuario=usuario, acao="CANCELAR_PEDIDO_COMPRA", modulo="Compras", objeto=str(pedido),
            dados_novos={"motivo": motivo},
        )
        return pedido
