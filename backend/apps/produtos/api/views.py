from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError as DRFValidationError
from rest_framework.filters import SearchFilter
from rest_framework.response import Response

from django_filters.rest_framework import DjangoFilterBackend

from ..models import Categoria, Fabricante, Produto
from ..permissions import PodeGerenciarProdutos
from ..serializers import CategoriaSerializer, FabricanteSerializer, ProdutoSerializer
from ..services import ProdutoService


def _traduzir_erro(func):
    """Converte ValidationError do Django (levantada no service/model) em
    ValidationError do DRF, para a API responder 400 em vez de 500."""

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except DjangoValidationError as exc:
            raise DRFValidationError(exc.messages if hasattr(exc, "messages") else str(exc))

    return wrapper


class ProdutoViewSet(viewsets.ModelViewSet):
    serializer_class = ProdutoSerializer
    permission_classes = [PodeGerenciarProdutos]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ["categoria", "fabricante", "ativo", "controla_lote"]
    search_fields = ["codigo_interno", "codigo_barras", "nome"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service = ProdutoService()

    def get_queryset(self):
        return self.service.listar()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        produto = self._criar(criado_por=request.user, **serializer.validated_data)
        return Response(ProdutoSerializer(produto).data, status=201)

    @_traduzir_erro
    def _criar(self, **kwargs):
        return self.service.criar_produto(**kwargs)

    def update(self, request, *args, **kwargs):
        produto = self.get_object()
        serializer = self.get_serializer(produto, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        produto = self._atualizar(produto=produto, atualizado_por=request.user, **serializer.validated_data)
        return Response(ProdutoSerializer(produto).data)

    @_traduzir_erro
    def _atualizar(self, **kwargs):
        return self.service.atualizar_produto(**kwargs)

    def destroy(self, request, *args, **kwargs):
        produto = self.get_object()
        self.service.desativar_produto(produto=produto, executor=request.user)
        return Response(status=204)


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [PodeGerenciarProdutos]


class FabricanteViewSet(viewsets.ModelViewSet):
    queryset = Fabricante.objects.all()
    serializer_class = FabricanteSerializer
    permission_classes = [PodeGerenciarProdutos]
