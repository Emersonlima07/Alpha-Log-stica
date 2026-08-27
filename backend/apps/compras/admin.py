from django.contrib import admin

from .models import Cotacao, PedidoCompra, PedidoCompraItem, SolicitacaoCompra


class CotacaoInline(admin.TabularInline):
    model = Cotacao
    extra = 0


@admin.register(SolicitacaoCompra)
class SolicitacaoCompraAdmin(admin.ModelAdmin):
    list_display = ("id", "produto", "filial", "quantidade_solicitada", "status", "solicitante")
    list_filter = ("status", "filial")
    inlines = [CotacaoInline]


class PedidoCompraItemInline(admin.TabularInline):
    model = PedidoCompraItem
    extra = 0


@admin.register(PedidoCompra)
class PedidoCompraAdmin(admin.ModelAdmin):
    list_display = ("numero", "fornecedor", "filial", "status", "valor_total", "data_pedido")
    list_filter = ("status", "filial")
    inlines = [PedidoCompraItemInline]
