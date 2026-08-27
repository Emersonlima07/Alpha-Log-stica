from rest_framework import serializers

from .models import Cotacao, PedidoCompra, PedidoCompraItem, SolicitacaoCompra


class CotacaoSerializer(serializers.ModelSerializer):
    fornecedor_nome = serializers.CharField(source="fornecedor.__str__", read_only=True)

    class Meta:
        model = Cotacao
        fields = [
            "id", "solicitacao", "fornecedor", "fornecedor_nome", "valor_unitario",
            "prazo_entrega_dias", "condicoes_pagamento", "selecionada", "criado_em",
        ]
        read_only_fields = ["id", "selecionada", "criado_em"]


class SolicitacaoCompraSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    filial_nome = serializers.CharField(source="filial.nome", read_only=True)
    solicitante_nome = serializers.CharField(source="solicitante.__str__", read_only=True)
    cotacoes = CotacaoSerializer(many=True, read_only=True)

    class Meta:
        model = SolicitacaoCompra
        fields = [
            "id", "produto", "produto_nome", "filial", "filial_nome", "quantidade_solicitada",
            "solicitante", "solicitante_nome", "motivo", "status", "aprovado_por",
            "observacao_aprovacao", "cotacoes", "criado_em",
        ]
        read_only_fields = ["id", "status", "aprovado_por", "observacao_aprovacao", "criado_em"]


class PedidoCompraItemSerializer(serializers.ModelSerializer):
    produto_nome = serializers.CharField(source="produto.nome", read_only=True)
    quantidade_pendente = serializers.DecimalField(max_digits=14, decimal_places=3, read_only=True)

    class Meta:
        model = PedidoCompraItem
        fields = ["id", "produto", "produto_nome", "quantidade", "valor_unitario", "quantidade_recebida", "quantidade_pendente"]
        read_only_fields = fields


class PedidoCompraSerializer(serializers.ModelSerializer):
    fornecedor_nome = serializers.CharField(source="fornecedor.__str__", read_only=True)
    filial_nome = serializers.CharField(source="filial.nome", read_only=True)
    itens = PedidoCompraItemSerializer(many=True, read_only=True)

    class Meta:
        model = PedidoCompra
        fields = [
            "id", "numero", "fornecedor", "fornecedor_nome", "filial", "filial_nome",
            "solicitacao_origem", "status", "data_pedido", "data_prevista_entrega",
            "criado_por", "valor_total", "itens", "criado_em",
        ]
        read_only_fields = fields
