from rest_framework import serializers

from .models import Empresa, Filial


class FilialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filial
        fields = ["id", "empresa", "codigo", "nome", "endereco", "ativo", "criado_em"]
        read_only_fields = ["id", "criado_em"]


class EmpresaSerializer(serializers.ModelSerializer):
    filiais = FilialSerializer(many=True, read_only=True)

    class Meta:
        model = Empresa
        fields = [
            "id",
            "razao_social",
            "nome_fantasia",
            "cnpj",
            "ativo",
            "criado_em",
            "filiais",
        ]
        read_only_fields = ["id", "criado_em"]
