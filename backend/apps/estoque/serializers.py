from rest_framework import serializers

from .models import Lote, MovimentoEstoque


class LoteSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    filial_nome = serializers.CharField(source="filial.nome", read_only=True)

    class Meta:
        model = Lote
        fields = [
            "id", "produto", "produto_nome", "filial", "filial_nome",
            "numero_lote", "data_validade", "quantidade_atual", "valor_unitario",
        ]
        read_only_fields = fields


class MovimentoEstoqueSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    usuario_nome = serializers.CharField(source="usuario.__str__", read_only=True)

    class Meta:
        model = MovimentoEstoque
        fields = [
            "id", "tipo", "produto", "produto_nome", "lote", "quantidade",
            "filial_origem", "filial_destino", "motivo", "usuario", "usuario_nome", "criado_em",
        ]
        read_only_fields = fields


class EntradaEstoqueSerializer(serializers.Serializer):
    produto = serializers.IntegerField()
    filial = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=14, decimal_places=3)
    numero_lote = serializers.CharField(required=False, allow_blank=True)
    data_validade = serializers.DateField(required=False, allow_null=True)
    valor_unitario = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    motivo = serializers.CharField(required=False, allow_blank=True)


class SaidaEstoqueSerializer(serializers.Serializer):
    produto = serializers.IntegerField()
    filial = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=14, decimal_places=3)
    numero_lote = serializers.CharField(required=False, allow_blank=True)
    motivo = serializers.CharField(required=False, allow_blank=True)


class BaixaEstoqueSerializer(SaidaEstoqueSerializer):
    motivo = serializers.CharField(required=True, allow_blank=False)


class TransferenciaEstoqueSerializer(serializers.Serializer):
    produto = serializers.IntegerField()
    filial_origem = serializers.IntegerField()
    filial_destino = serializers.IntegerField()
    quantidade = serializers.DecimalField(max_digits=14, decimal_places=3)
    numero_lote = serializers.CharField(required=False, allow_blank=True)
    motivo = serializers.CharField(required=False, allow_blank=True)


class AjusteEstoqueSerializer(serializers.Serializer):
    produto = serializers.IntegerField()
    filial = serializers.IntegerField()
    nova_quantidade = serializers.DecimalField(max_digits=14, decimal_places=3)
    numero_lote = serializers.CharField(required=False, allow_blank=True)
    motivo = serializers.CharField(required=True, allow_blank=False)
