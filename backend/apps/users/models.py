from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.db import models

from apps.core.models import BaseModel, Empresa, Filial


class UserManager(DjangoUserManager):
    """
    Combina o manager padrao do Django (que sabe criar create_user/
    create_superuser com senha hasheada) com o filtro de Soft Delete.
    Necessario porque, em heranca multipla, o manager de AbstractUser
    teria prioridade sobre o SoftDeleteManager do BaseModel e mascararia
    o soft delete de usuarios.
    """

    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class Perfil(models.TextChoices):
    """
    Os 5 perfis definidos na especificacao (Modulo 16). Mantido como
    choices (e nao tabela) porque as regras de cada perfil sao fixas
    no sistema; granularidade adicional de permissao por modulo pode
    ser adicionada depois via um modelo Permissao dedicado sem quebrar
    este contrato.
    """

    ADMINISTRADOR = "administrador", "Administrador"
    SUPERVISOR = "supervisor", "Supervisor"
    OPERADOR_LOGISTICO = "operador_logistico", "Operador/Tecnico de Logistica"
    COMPRADOR = "comprador", "Comprador"
    DIRETORIA = "diretoria", "Diretoria"


class User(AbstractUser, BaseModel):
    """
    Usuario do ERP. Sempre vinculado a uma empresa (multiempresa) e,
    opcionalmente, a uma filial especifica. `perfil` determina o que o
    usuario pode acessar (ver apps/users/permissions.py).
    """

    perfil = models.CharField(max_length=30, choices=Perfil.choices)
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, related_name="usuarios", null=True, blank=True
    )
    filial = models.ForeignKey(
        Filial, on_delete=models.SET_NULL, related_name="usuarios", null=True, blank=True
    )
    telefone = models.CharField(max_length=20, blank=True)

    objects = UserManager()
    todos_objects = DjangoUserManager()  # inclui inativos (uso administrativo/auditoria)

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["username"]

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_administrador_ou_diretoria(self):
        return self.perfil in (Perfil.ADMINISTRADOR, Perfil.DIRETORIA)
