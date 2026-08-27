from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Filial
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto

from ..models import Cotacao, PedidoCompra, SolicitacaoCompra
from ..permissions import PodeAprovarCompra, PodeSolicitarCompra
from ..serializers import (
    CotacaoSerializer,
    PedidoCompraSerializer,
    SolicitacaoCompraSerializer,
)
from ..services import ComprasService


def _traduzir_erro(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages if hasattr(exc, "messages") else str(exc))
    return wrapper


class SolicitacaoCompraViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Leitura via ViewSet (list/retrieve). As transicoes de estado
    (criar, cotar, aprovar, rejeitar) sao acoes explicitas abaixo --
    fica mais claro na API do que sobrecarregar um PATCH generico.
    """

    queryset = SolicitacaoCompra.objects.select_related("produto", "filial", "solicitante").prefetch_related("cotacoes")
    serializer_class = SolicitacaoCompraSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "produto", "filial"]


class PedidoCompraViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PedidoCompra.objects.select_related("fornecedor", "filial").prefetch_related("itens")
    serializer_class = PedidoCompraSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "fornecedor", "filial"]


class CriarSolicitacaoView(APIView):
    permission_classes = [PodeSolicitarCompra]

    @_traduzir_erro
    def post(self, request):
        produto = get_object_or_404(Produto, id=request.data.get("produto"))
        filial = get_object_or_404(Filial, id=request.data.get("filial"))
        solicitacao = ComprasService().criar_solicitacao(
            produto=produto, filial=filial, quantidade_solicitada=request.data.get("quantidade_solicitada"),
            solicitante=request.user, motivo=request.data.get("motivo", ""),
        )
        return Response(SolicitacaoCompraSerializer(solicitacao).data, status=201)


class AdicionarCotacaoView(APIView):
    permission_classes = [PodeSolicitarCompra]

    @_traduzir_erro
    def post(self, request, solicitacao_id):
        solicitacao = get_object_or_404(SolicitacaoCompra, id=solicitacao_id)
        fornecedor = get_object_or_404(Fornecedor, id=request.data.get("fornecedor"))
        cotacao = ComprasService().adicionar_cotacao(
            solicitacao=solicitacao, fornecedor=fornecedor, valor_unitario=request.data.get("valor_unitario"),
            usuario=request.user, prazo_entrega_dias=request.data.get("prazo_entrega_dias", 0),
            condicoes_pagamento=request.data.get("condicoes_pagamento", ""),
        )
        return Response(CotacaoSerializer(cotacao).data, status=201)


class SelecionarCotacaoView(APIView):
    permission_classes = [PodeSolicitarCompra]

    @_traduzir_erro
    def post(self, request, cotacao_id):
        cotacao = get_object_or_404(Cotacao, id=cotacao_id)
        cotacao = ComprasService().selecionar_cotacao(cotacao=cotacao, usuario=request.user)
        return Response(CotacaoSerializer(cotacao).data)


class AprovarSolicitacaoView(APIView):
    permission_classes = [PodeAprovarCompra]

    @_traduzir_erro
    def post(self, request, solicitacao_id):
        solicitacao = get_object_or_404(SolicitacaoCompra, id=solicitacao_id)
        pedido = ComprasService().aprovar_solicitacao(
            solicitacao=solicitacao, aprovador=request.user, observacao=request.data.get("observacao", ""),
        )
        return Response(PedidoCompraSerializer(pedido).data, status=201)


class RejeitarSolicitacaoView(APIView):
    permission_classes = [PodeAprovarCompra]

    @_traduzir_erro
    def post(self, request, solicitacao_id):
        solicitacao = get_object_or_404(SolicitacaoCompra, id=solicitacao_id)
        solicitacao = ComprasService().rejeitar_solicitacao(
            solicitacao=solicitacao, aprovador=request.user, motivo=request.data.get("motivo", ""),
        )
        return Response(SolicitacaoCompraSerializer(solicitacao).data)


class EnviarPedidoView(APIView):
    permission_classes = [PodeSolicitarCompra]

    @_traduzir_erro
    def post(self, request, pedido_id):
        pedido = get_object_or_404(PedidoCompra, id=pedido_id)
        pedido = ComprasService().marcar_pedido_enviado(pedido=pedido, usuario=request.user)
        return Response(PedidoCompraSerializer(pedido).data)


class CancelarPedidoView(APIView):
    permission_classes = [PodeAprovarCompra]

    @_traduzir_erro
    def post(self, request, pedido_id):
        pedido = get_object_or_404(PedidoCompra, id=pedido_id)
        pedido = ComprasService().cancelar_pedido(pedido=pedido, usuario=request.user, motivo=request.data.get("motivo", ""))
        return Response(PedidoCompraSerializer(pedido).data)
