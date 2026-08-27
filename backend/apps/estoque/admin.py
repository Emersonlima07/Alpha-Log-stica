from django.contrib import admin

from .models import Lote, MovimentoEstoque


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ("produto", "filial", "numero_lote", "data_validade", "quantidade_atual", "valor_unitario")
    list_filter = ("filial",)
    search_fields = ("produto__codigo_interno", "produto__nome", "numero_lote")


@admin.register(MovimentoEstoque)
class MovimentoEstoqueAdmin(admin.ModelAdmin):
    list_display = ("criado_em", "tipo", "produto", "quantidade", "filial_origem", "filial_destino", "usuario")
    list_filter = ("tipo", "filial_origem", "filial_destino")
    search_fields = ("produto__codigo_interno", "produto__nome")
    readonly_fields = [f.name for f in MovimentoEstoque._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
