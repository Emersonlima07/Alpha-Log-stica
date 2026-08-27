from rest_framework import serializers

from .models import Fornecedor


class FornecedorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Fornecedor
        fields = [
            "id", "razao_social", "nome_fantasia", "cnpj", "telefone", "email", "endereco",
            "contato_nome", "prazo_pagamento_padrao_dias", "avaliacao_pontualidade",
            "avaliacao_qualidade", "observacoes", "ativo", "criado_em",
        ]
        read_only_fields = ["id", "avaliacao_pontualidade", "avaliacao_qualidade", "criado_em"]
