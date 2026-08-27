from django.contrib import admin

from .models import Categoria, Fabricante, Produto


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)


@admin.register(Fabricante)
class FabricanteAdmin(admin.ModelAdmin):
    list_display = ("nome", "ativo")
    search_fields = ("nome",)


@admin.register(Produto)
class ProdutoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_interno",
        "nome",
        "categoria",
        "fabricante",
        "unidade_medida",
        "estoque_minimo",
        "estoque_maximo",
        "ativo",
    )
    list_filter = ("categoria", "fabricante", "unidade_medida", "ativo")
    search_fields = ("codigo_interno", "codigo_barras", "nome")
