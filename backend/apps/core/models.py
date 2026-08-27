from django.db import models


class SoftDeleteManager(models.Manager):
    """Retorna apenas registros ativos por padrao (Soft Delete)."""

    def get_queryset(self):
        return super().get_queryset().filter(ativo=True)


class BaseModel(models.Model):
    """
    Modelo base para todo o ERP.

    Todo modulo deve herdar deste modelo para garantir, de forma
    consistente: timestamps de auditoria, soft delete e um manager
    padrao que ja filtra registros excluidos.
    """

    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)
    ativo = models.BooleanField(default=True)

    objects = SoftDeleteManager()
    todos_objects = models.Manager()  # inclui inativos, uso administrativo/auditoria

    class Meta:
        abstract = True

    def deletar(self):
        """Soft delete: nunca remove fisicamente o registro do banco."""
        self.ativo = False
        self.save(update_fields=["ativo", "atualizado_em"])

    def restaurar(self):
        self.ativo = True
        self.save(update_fields=["ativo", "atualizado_em"])


class Empresa(BaseModel):
    razao_social = models.CharField(max_length=255)
    nome_fantasia = models.CharField(max_length=255, blank=True)
    cnpj = models.CharField(max_length=18, unique=True)

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["razao_social"]

    def __str__(self):
        return self.nome_fantasia or self.razao_social


class Filial(BaseModel):
    empresa = models.ForeignKey(Empresa, on_delete=models.PROTECT, related_name="filiais")
    codigo = models.CharField(max_length=20)
    nome = models.CharField(max_length=255)
    endereco = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Filial"
        verbose_name_plural = "Filiais"
        unique_together = ("empresa", "codigo")
        ordering = ["nome"]

    def __str__(self):
        return f"{self.nome} ({self.empresa})"
