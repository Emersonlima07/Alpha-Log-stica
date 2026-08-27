from django.core.exceptions import ValidationError
from django.db import models

from apps.core.models import BaseModel


class Categoria(BaseModel):
    nome = models.CharField(max_length=100, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Fabricante(BaseModel):
    nome = models.CharField(max_length=150, unique=True)

    class Meta:
        verbose_name = "Fabricante"
        verbose_name_plural = "Fabricantes"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class UnidadeMedida(models.TextChoices):
    UNIDADE = "UN", "Unidade"
    CAIXA = "CX", "Caixa"
    QUILOGRAMA = "KG", "Quilograma"
    GRAMA = "G", "Grama"
    LITRO = "L", "Litro"
    MILILITRO = "ML", "Mililitro"
    METRO = "M", "Metro"
    PACOTE = "PCT", "Pacote"


class Produto(BaseModel):
    codigo_interno = models.CharField(max_length=50, unique=True)
    codigo_barras = models.CharField(max_length=50, blank=True, db_index=True)
    nome = models.CharField(max_length=255)
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name="produtos", null=True, blank=True)
    fabricante = models.ForeignKey(Fabricante, on_delete=models.PROTECT, related_name="produtos", null=True, blank=True)
    unidade_medida = models.CharField(max_length=5, choices=UnidadeMedida.choices, default=UnidadeMedida.UNIDADE)
    controla_lote = models.BooleanField(default=True)

    valor_compra = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    valor_medio = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    estoque_minimo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    estoque_maximo = models.DecimalField(max_digits=12, decimal_places=3, default=0)
    estoque_seguranca = models.DecimalField(max_digits=12, decimal_places=3, default=0)

    # Modulo 4 (Compras) ja implementado: referencia real ao cadastro de Fornecedor.
    fornecedor_principal = models.ForeignKey(
        "fornecedores.Fornecedor", on_delete=models.SET_NULL, null=True, blank=True, related_name="produtos"
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["nome"]

    def __str__(self):
        return f"{self.codigo_interno} - {self.nome}"

    def clean(self):
        if self.estoque_maximo and self.estoque_minimo and self.estoque_maximo < self.estoque_minimo:
            raise ValidationError("Estoque maximo nao pode ser menor que o estoque minimo.")

    @property
    def quantidade_total_em_estoque(self):
        return self.lotes.aggregate(total=models.Sum("quantidade_atual"))["total"] or 0
