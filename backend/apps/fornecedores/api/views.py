from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.response import Response

from ..models import Fornecedor
from ..permissions import PodeGerenciarFornecedores
from ..serializers import FornecedorSerializer
from ..services import FornecedorService


def _traduzir_erro(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages if hasattr(exc, "messages") else str(exc))
    return wrapper


class FornecedorViewSet(viewsets.ModelViewSet):
    serializer_class = FornecedorSerializer
    permission_classes = [PodeGerenciarFornecedores]
    filterset_fields = ["ativo"]
    search_fields = ["razao_social", "nome_fantasia", "cnpj"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = FornecedorService()

    def get_queryset(self):
        return self.service.listar()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        fornecedor = self._criar(criado_por=request.user, **serializer.validated_data)
        return Response(FornecedorSerializer(fornecedor).data, status=201)

    @_traduzir_erro
    def _criar(self, **kwargs):
        return self.service.criar_fornecedor(**kwargs)

    def update(self, request, *args, **kwargs):
        fornecedor = self.get_object()
        serializer = self.get_serializer(fornecedor, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        fornecedor = self.service.atualizar_fornecedor(fornecedor=fornecedor, atualizado_por=request.user, **serializer.validated_data)
        return Response(FornecedorSerializer(fornecedor).data)

    def destroy(self, request, *args, **kwargs):
        fornecedor = self.get_object()
        self.service.desativar_fornecedor(fornecedor=fornecedor, executor=request.user)
        return Response(status=204)

    @action(detail=True, methods=["post"])
    def avaliar(self, request, pk=None):
        fornecedor = self.get_object()
        fornecedor = self.service.avaliar_fornecedor(
            fornecedor=fornecedor, avaliador=request.user,
            pontualidade=request.data.get("pontualidade"), qualidade=request.data.get("qualidade"),
        )
        return Response(FornecedorSerializer(fornecedor).data)
