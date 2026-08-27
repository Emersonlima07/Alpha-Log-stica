from django.core.exceptions import ValidationError as DjangoValidationError
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.compras.models import PedidoCompra

from ..models import Recebimento, RecebimentoItem
from ..permissions import PodeAprovarRecebimento, PodeReceber
from ..serializers import RecebimentoItemSerializer, RecebimentoSerializer
from ..services import RecebimentoService


def _traduzir_erro(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages if hasattr(exc, "messages") else str(exc))
    return wrapper


class RecebimentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Recebimento.objects.select_related("pedido_compra", "responsavel").prefetch_related("itens")
    serializer_class = RecebimentoSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ["status", "pedido_compra"]


class IniciarRecebimentoView(APIView):
    permission_classes = [PodeReceber]

    @_traduzir_erro
    def post(self, request):
        pedido = get_object_or_404(PedidoCompra, id=request.data.get("pedido_compra"))
        recebimento = RecebimentoService().iniciar_recebimento(
            pedido_compra=pedido, responsavel=request.user,
            numero_nf=request.data.get("numero_nf", ""), chave_nfe=request.data.get("chave_nfe", ""),
        )
        return Response(RecebimentoSerializer(recebimento).data, status=201)


class ImportarXmlNfeView(APIView):
    permission_classes = [PodeReceber]

    @_traduzir_erro
    def post(self, request):
        pedido = get_object_or_404(PedidoCompra, id=request.data.get("pedido_compra"))
        xml_content = request.data.get("xml_content", "")
        if not xml_content:
            raise DRFValidationError("Envie o conteudo do XML no campo 'xml_content'.")
        recebimento = RecebimentoService().importar_xml_nfe(
            pedido_compra=pedido, xml_content=xml_content, responsavel=request.user,
        )
        return Response(RecebimentoSerializer(recebimento).data, status=201)


class ConferirItemView(APIView):
    permission_classes = [PodeReceber]

    @_traduzir_erro
    def post(self, request, item_id):
        item = get_object_or_404(RecebimentoItem, id=item_id)
        item = RecebimentoService().conferir_item(
            item=item, quantidade_conferida=request.data.get("quantidade_conferida"), usuario=request.user,
            numero_lote=request.data.get("numero_lote", ""), data_validade=request.data.get("data_validade"),
        )
        return Response(RecebimentoItemSerializer(item).data)


class AprovarRecebimentoView(APIView):
    permission_classes = [PodeAprovarRecebimento]

    @_traduzir_erro
    def post(self, request, recebimento_id):
        recebimento = get_object_or_404(Recebimento, id=recebimento_id)
        recebimento = RecebimentoService().aprovar_recebimento(recebimento=recebimento, aprovador=request.user)
        return Response(RecebimentoSerializer(recebimento).data)


class RejeitarRecebimentoView(APIView):
    permission_classes = [PodeAprovarRecebimento]

    @_traduzir_erro
    def post(self, request, recebimento_id):
        recebimento = get_object_or_404(Recebimento, id=recebimento_id)
        recebimento = RecebimentoService().rejeitar_recebimento(
            recebimento=recebimento, aprovador=request.user, motivo=request.data.get("motivo", ""),
        )
        return Response(RecebimentoSerializer(recebimento).data)
