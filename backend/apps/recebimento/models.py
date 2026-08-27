from django.db import models

from apps.compras.models import PedidoCompra, PedidoCompraItem
from apps.core.models import BaseModel
from apps.produtos.models import Produto


class StatusRecebimento(models.TextChoices):
    EM_CONFERENCIA = "EM_CONFERENCIA", "Em conferência"
    APROVADO = "APROVADO", "Aprovado"
    REJEITADO = "REJEITADO", "Rejeitado (divergência)"


class Recebimento(BaseModel):
    """
    Um evento de recebimento de mercadoria contra um Pedido de Compra
    (Modulo 5). Um pedido pode ter mais de um recebimento se a entrega
    vier parcelada. Ao ser aprovado, cada item confere gera entrada
    automatica no estoque (Modulo 3), sem re-digitar nada.
    """

    pedido_compra = models.ForeignKey(PedidoCompra, on_delete=models.PROTECT, related_name="recebimentos")
    numero_nf = models.CharField(max_length=50, blank=True)
    chave_nfe = models.CharField(max_length=44, blank=True, help_text="Chave de acesso da NF-e (44 digitos), se houver.")
    status = models.CharField(max_length=20, choices=StatusRecebimento.choices, default=StatusRecebimento.EM_CONFERENCIA)
    responsavel = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True, related_name="recebimentos")
    data_recebimento = models.DateTimeField(auto_now_add=True)
    observacoes = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Recebimento"
        verbose_name_plural = "Recebimentos"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Recebimento #{self.id} - Pedido {self.pedido_compra.numero} ({self.status})"

    @property
    def tem_divergencia(self):
        return any(item.tem_divergencia for item in self.itens.all())


class RecebimentoItem(BaseModel):
    recebimento = models.ForeignKey(Recebimento, on_delete=models.CASCADE, related_name="itens")
    pedido_item = models.ForeignKey(PedidoCompraItem, on_delete=models.PROTECT, related_name="itens_recebidos", null=True, blank=True)
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="itens_recebimento")

    quantidade_nf = models.DecimalField(max_digits=14, decimal_places=3, help_text="Quantidade informada na nota fiscal.")
    quantidade_conferida = models.DecimalField(max_digits=14, decimal_places=3, default=0, help_text="Quantidade contada fisicamente.")
    numero_lote = models.CharField(max_length=50, blank=True)
    data_validade = models.DateField(null=True, blank=True)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Item do Recebimento"
        verbose_name_plural = "Itens do Recebimento"

    def __str__(self):
        return f"{self.produto.codigo_interno}: NF {self.quantidade_nf} / conferido {self.quantidade_conferida}"

    @property
    def tem_divergencia(self):
        return self.quantidade_conferida != self.quantidade_nf
