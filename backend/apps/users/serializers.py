from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "perfil",
            "empresa",
            "filial",
            "telefone",
            "ativo",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "password",
            "first_name",
            "last_name",
            "email",
            "perfil",
            "empresa",
            "filial",
            "telefone",
        ]
        read_only_fields = ["id"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Inclui perfil e empresa no payload do token, para o frontend
    montar o menu correto sem precisar de uma segunda chamada."""

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["perfil"] = user.perfil
        token["empresa_id"] = user.empresa_id
        token["nome"] = user.get_full_name() or user.username
        return token
