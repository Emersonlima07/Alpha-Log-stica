from rest_framework import serializers

from .models import Categoria, Fabricante, Produto


class CategoriaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categoria
        fields = ["id", "nome", "ativo"]
        read_only_fields = ["id"]


class FabricanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fabricante
        fields = ["id", "nome", "ativo"]
        read_only_fields = ["id"]


class ProdutoSerializer(serializers.ModelSerializer):
    categoria_nome = serializers.CharField(source="categoria.nome", read_only=True, default=None)
    fabricante_nome = serializers.CharField(source="fabricante.nome", read_only=True, default=None)
    fornecedor_principal_nome = serializers.CharField(source="fornecedor_principal.nome_fantasia", read_only=True, default=None)
    quantidade_total_em_estoque = serializers.DecimalField(max_digits=12, decimal_places=3, read_only=True)

    class Meta:
        model = Produto
        fields = [
            "id", "codigo_interno", "codigo_barras", "nome", "categoria", "categoria_nome",
            "fabricante", "fabricante_nome", "unidade_medida", "controla_lote", "valor_compra",
            "valor_medio", "estoque_minimo", "estoque_maximo", "estoque_seguranca",
            "fornecedor_principal", "fornecedor_principal_nome", "quantidade_total_em_estoque",
            "ativo", "criado_em",
        ]
        read_only_fields = ["id", "valor_medio", "criado_em"]
