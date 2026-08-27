from django.contrib import admin

from .models import Empresa, Filial


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("razao_social", "nome_fantasia", "cnpj", "ativo")
    search_fields = ("razao_social", "nome_fantasia", "cnpj")


@admin.register(Filial)
class FilialAdmin(admin.ModelAdmin):
    list_display = ("nome", "codigo", "empresa", "ativo")
    list_filter = ("empresa",)
