from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.core.models import Filial
from apps.produtos.models import Produto

from ..models import Lote, MovimentoEstoque
from ..permissions import PodeAjustarEstoque, PodeMovimentarEstoque
from ..serializers import (
    AjusteEstoqueSerializer,
    BaixaEstoqueSerializer,
    EntradaEstoqueSerializer,
    LoteSerializer,
    MovimentoEstoqueSerializer,
    SaidaEstoqueSerializer,
    TransferenciaEstoqueSerializer,
)
from ..services import EstoqueService


def _traduzir_erro(func):
    """Converte ValidationError do Django (usada no service layer) em
    ValidationError do DRF, para que a API devolva HTTP 400 com a
    mensagem certa em vez de um HTTP 500."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages if hasattr(exc, "messages") else str(exc))

    return wrapper


class LoteViewSet(viewsets.ReadOnlyModelViewSet):
    """Consulta de lotes (Modulo 3: consulta por lote / por validade)."""

    queryset = Lote.objects.select_related("produto", "filial").filter(quantidade_atual__gt=0)
    serializer_class = LoteSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["produto", "filial", "numero_lote"]


class MovimentoEstoqueViewSet(viewsets.ReadOnlyModelViewSet):
    """Historico completo de movimentacoes (Modulo 3)."""

    queryset = MovimentoEstoque.objects.select_related("produto", "lote", "usuario").all()
    serializer_class = MovimentoEstoqueSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["produto", "tipo", "filial_origem", "filial_destino"]


class ProdutosVencendoView(APIView):
    """GET /api/estoque/vencendo/?ate=YYYY-MM-DD -- lotes vencendo ate a data informada."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        data_limite = request.query_params.get("ate")
        if not data_limite:
            raise DRFValidationError("Informe o parametro 'ate' (YYYY-MM-DD).")
        service = EstoqueService()
        lotes = service.consultar_por_validade(data_limite)
        return Response(LoteSerializer(lotes, many=True).data)


class EntradaEstoqueView(APIView):
    permission_classes = [PodeMovimentarEstoque]

    @_traduzir_erro
    def post(self, request):
        serializer = EntradaEstoqueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = get_object_or_404(Produto, id=dados["produto"])
        filial = get_object_or_404(Filial, id=dados["filial"])

        movimento = EstoqueService().registrar_entrada(
            produto=produto,
            filial=filial,
            quantidade=dados["quantidade"],
            usuario=request.user,
            numero_lote=dados.get("numero_lote"),
            data_validade=dados.get("data_validade"),
            valor_unitario=dados.get("valor_unitario"),
            motivo=dados.get("motivo", ""),
        )
        return Response(MovimentoEstoqueSerializer(movimento).data, status=201)


class SaidaEstoqueView(APIView):
    permission_classes = [PodeMovimentarEstoque]

    @_traduzir_erro
    def post(self, request):
        serializer = SaidaEstoqueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = get_object_or_404(Produto, id=dados["produto"])
        filial = get_object_or_404(Filial, id=dados["filial"])

        movimento = EstoqueService().registrar_saida(
            produto=produto,
            filial=filial,
            quantidade=dados["quantidade"],
            usuario=request.user,
            numero_lote=dados.get("numero_lote"),
            motivo=dados.get("motivo", ""),
        )
        return Response(MovimentoEstoqueSerializer(movimento).data, status=201)


class BaixaEstoqueView(APIView):
    permission_classes = [PodeMovimentarEstoque]

    @_traduzir_erro
    def post(self, request):
        serializer = BaixaEstoqueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = get_object_or_404(Produto, id=dados["produto"])
        filial = get_object_or_404(Filial, id=dados["filial"])

        movimento = EstoqueService().dar_baixa(
            produto=produto,
            filial=filial,
            quantidade=dados["quantidade"],
            usuario=request.user,
            numero_lote=dados.get("numero_lote"),
            motivo=dados.get("motivo", ""),
        )
        return Response(MovimentoEstoqueSerializer(movimento).data, status=201)


class TransferenciaEstoqueView(APIView):
    permission_classes = [PodeMovimentarEstoque]

    @_traduzir_erro
    def post(self, request):
        serializer = TransferenciaEstoqueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = get_object_or_404(Produto, id=dados["produto"])
        filial_origem = get_object_or_404(Filial, id=dados["filial_origem"])
        filial_destino = get_object_or_404(Filial, id=dados["filial_destino"])

        movimento = EstoqueService().transferir(
            produto=produto,
            filial_origem=filial_origem,
            filial_destino=filial_destino,
            quantidade=dados["quantidade"],
            usuario=request.user,
            numero_lote=dados.get("numero_lote"),
            motivo=dados.get("motivo", ""),
        )
        return Response(MovimentoEstoqueSerializer(movimento).data, status=201)


class AjusteEstoqueView(APIView):
    permission_classes = [PodeAjustarEstoque]

    @_traduzir_erro
    def post(self, request):
        serializer = AjusteEstoqueSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        dados = serializer.validated_data
        produto = get_object_or_404(Produto, id=dados["produto"])
        filial = get_object_or_404(Filial, id=dados["filial"])

        movimento = EstoqueService().ajustar(
            produto=produto,
            filial=filial,
            nova_quantidade=dados["nova_quantidade"],
            usuario=request.user,
            numero_lote=dados.get("numero_lote"),
            motivo=dados["motivo"],
        )
        return Response(MovimentoEstoqueSerializer(movimento).data, status=201)
