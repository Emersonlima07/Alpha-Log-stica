from rest_framework import serializers

from .models import LogAuditoria


class LogAuditoriaSerializer(serializers.ModelSerializer):
    usuario_nome = serializers.CharField(source="usuario.__str__", read_only=True)

    class Meta:
        model = LogAuditoria
        fields = [
            "id",
            "usuario",
            "usuario_nome",
            "acao",
            "modulo",
            "objeto",
            "dados_anteriores",
            "dados_novos",
            "ip",
            "criado_em",
        ]
        read_only_fields = fields
