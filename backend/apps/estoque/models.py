from django.db import models

from apps.core.models import BaseModel, Filial
from apps.produtos.models import Produto


class Lote(BaseModel):
    """
    Representa uma remessa fisica de um produto numa filial: quanto tem
    (quantidade_atual), a validade dela e o custo unitario de aquisicao.
    Um produto pode ter varios lotes ativos ao mesmo tempo. Produtos que
    nao controlam lote (Produto.controla_lote=False) ainda usam este
    modelo, mas com numero_lote fixo em "UNICO".
    """

    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="lotes")
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT, related_name="lotes")
    numero_lote = models.CharField(max_length=50, default="UNICO")
    data_validade = models.DateField(null=True, blank=True)
    quantidade_atual = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Lote"
        verbose_name_plural = "Lotes"
        unique_together = ("produto", "filial", "numero_lote")
        ordering = ["data_validade"]

    def __str__(self):
        return f"{self.produto.codigo_interno} / lote {self.numero_lote} / {self.filial.codigo}"


class TipoMovimento(models.TextChoices):
    ENTRADA = "ENTRADA", "Entrada"
    SAIDA = "SAIDA", "Saida"
    TRANSFERENCIA = "TRANSFERENCIA", "Transferencia"
    AJUSTE = "AJUSTE", "Ajuste"
    BAIXA = "BAIXA", "Baixa"


class MovimentoEstoque(BaseModel):
    """
    Historico completo e imutavel de toda movimentacao de estoque
    (Modulo 3). Cada linha aqui e um fato que ja aconteceu -- nunca e
    editada, apenas criada. Para ENTRADA/SAIDA/TRANSFERENCIA/BAIXA,
    `quantidade` e sempre positiva. Para AJUSTE, `quantidade` pode ser
    negativa (representa o delta aplicado: correcao pra cima ou pra baixo).
    """

    tipo = models.CharField(max_length=20, choices=TipoMovimento.choices)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="movimentos")
    lote = models.ForeignKey(Lote, on_delete=models.PROTECT, related_name="movimentos")
    quantidade = models.DecimalField(max_digits=14, decimal_places=3)
    filial_origem = models.ForeignKey(
        Filial, on_delete=models.PROTECT, related_name="movimentos_saida", null=True, blank=True
    )
    filial_destino = models.ForeignKey(
        Filial, on_delete=models.PROTECT, related_name="movimentos_entrada", null=True, blank=True
    )
    motivo = models.CharField(max_length=255, blank=True)
    usuario = models.ForeignKey(
        "users.User", on_delete=models.SET_NULL, null=True, related_name="movimentos_estoque"
    )

    class Meta:
        verbose_name = "Movimento de Estoque"
        verbose_name_plural = "Movimentos de Estoque"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.tipo} - {self.produto.codigo_interno} - {self.quantidade}"
