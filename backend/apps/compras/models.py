from django.conf import settings
from django.db import models

from apps.core.models import BaseModel, Empresa, Filial
from apps.fornecedores.models import Fornecedor
from apps.produtos.models import Produto


class StatusSolicitacao(models.TextChoices):
    PENDENTE = "PENDENTE", "Pendente"
    EM_COTACAO = "EM_COTACAO", "Em cotação"
    APROVADA = "APROVADA", "Aprovada"
    REJEITADA = "REJEITADA", "Rejeitada"
    CONVERTIDA = "CONVERTIDA", "Convertida em pedido"


class StatusPedido(models.TextChoices):
    ABERTO = "ABERTO", "Aberto"
    ENVIADO = "ENVIADO", "Enviado"
    RECEBIDO = "RECEBIDO", "Recebido"
    CANCELADO = "CANCELADO", "Cancelado"


class SolicitacaoCompra(BaseModel):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, related_name="solicitacoes_compra", editable=False
    )
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT, related_name="solicitacoes_compra")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="solicitacoes_compra")
    quantidade_solicitada = models.DecimalField(max_digits=14, decimal_places=3)
    solicitante = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="solicitacoes_compra"
    )
    motivo = models.TextField(blank=True, default="")
    status = models.CharField(max_length=20, choices=StatusSolicitacao.choices, default=StatusSolicitacao.PENDENTE)
    aprovado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="solicitacoes_aprovadas",
        null=True,
        blank=True,
    )
    observacao_aprovacao = models.TextField(blank=True, default="")

    class Meta:
        verbose_name = "Solicitação de compra"
        verbose_name_plural = "Solicitações de compra"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"Solicitação #{self.id} - {self.produto} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.filial_id and not self.empresa_id:
            self.empresa_id = self.filial.empresa_id
        super().save(*args, **kwargs)


class Cotacao(BaseModel):
    solicitacao = models.ForeignKey(SolicitacaoCompra, on_delete=models.CASCADE, related_name="cotacoes")
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name="cotacoes")
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    prazo_entrega_dias = models.PositiveIntegerField(default=0)
    condicoes_pagamento = models.CharField(max_length=100, blank=True, default="")
    selecionada = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Cotação"
        verbose_name_plural = "Cotações"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.fornecedor} - {self.valor_unitario}"


class PedidoCompra(BaseModel):
    empresa = models.ForeignKey(
        Empresa, on_delete=models.PROTECT, related_name="pedidos_compra", editable=False
    )
    filial = models.ForeignKey(Filial, on_delete=models.PROTECT, related_name="pedidos_compra")
    numero = models.CharField(max_length=20, unique=True, editable=False)
    fornecedor = models.ForeignKey(Fornecedor, on_delete=models.PROTECT, related_name="pedidos_compra")
    solicitacao_origem = models.ForeignKey(
        SolicitacaoCompra, on_delete=models.PROTECT, related_name="pedidos_gerados"
    )
    status = models.CharField(max_length=15, choices=StatusPedido.choices, default=StatusPedido.ABERTO)
    data_pedido = models.DateTimeField(auto_now_add=True)
    data_prevista_entrega = models.DateField(null=True, blank=True)
    criado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="pedidos_compra_criados"
    )
    valor_total = models.DecimalField(max_digits=14, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pedido de compra"
        verbose_name_plural = "Pedidos de compra"
        ordering = ["-criado_em"]

    def __str__(self):
        return f"{self.numero} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        if self.filial_id and not self.empresa_id:
            self.empresa_id = self.filial.empresa_id
        super().save(*args, **kwargs)


class PedidoCompraItem(BaseModel):
    pedido = models.ForeignKey(PedidoCompra, on_delete=models.CASCADE, related_name="itens")
    produto = models.ForeignKey(Produto, on_delete=models.PROTECT, related_name="itens_pedido_compra")
    quantidade = models.DecimalField(max_digits=14, decimal_places=3)
    valor_unitario = models.DecimalField(max_digits=12, decimal_places=2)
    quantidade_recebida = models.DecimalField(max_digits=14, decimal_places=3, default=0)

    class Meta:
        verbose_name = "Item do pedido de compra"
        verbose_name_plural = "Itens do pedido de compra"

    def __str__(self):
        return f"{self.produto} x {self.quantidade}"

    @property
    def quantidade_pendente(self):
        return self.quantidade - self.quantidade_recebida