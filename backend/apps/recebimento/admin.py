from django.contrib import admin

from .models import Recebimento, RecebimentoItem


class RecebimentoItemInline(admin.TabularInline):
    model = RecebimentoItem
    extra = 0


@admin.register(Recebimento)
class RecebimentoAdmin(admin.ModelAdmin):
    list_display = ("id", "pedido_compra", "numero_nf", "status", "responsavel", "data_recebimento")
    list_filter = ("status",)
    inlines = [RecebimentoItemInline]
