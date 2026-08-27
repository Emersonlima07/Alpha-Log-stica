from rest_framework import serializers

from .models import Recebimento, RecebimentoItem


class RecebimentoItemSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    tem_divergencia = serializers.BooleanField(read_only=True)

    class Meta:
        model = RecebimentoItem
        fields = [
            "id", "recebimento", "pedido_item", "produto", "produto_nome", "quantidade_nf",
            "quantidade_conferida", "numero_lote", "data_validade", "valor_unitario", "tem_divergencia",
        ]
        read_only_fields = ["id", "recebimento", "pedido_item", "produto", "produto_nome", "quantidade_nf", "valor_unitario", "tem_divergencia"]


class RecebimentoSerializer(serializers.ModelSerializer):
    pedido_numero = serializers.CharField(source="pedido_compra.numero", read_only=True)
    responsavel_nome = serializers.CharField(source="responsavel.__str__", read_only=True)
    itens = RecebimentoItemSerializer(many=True, read_only=True)
    tem_divergencia = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recebimento
        fields = [
            "id", "pedido_compra", "pedido_numero", "numero_nf", "chave_nfe", "status",
            "responsavel", "responsavel_nome", "data_recebimento", "observacoes", "itens", "tem_divergencia",
        ]
        read_only_fields = ["id", "status", "responsavel", "responsavel_nome", "data_recebimento", "tem_divergencia"]
