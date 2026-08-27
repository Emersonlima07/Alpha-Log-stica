from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/auth/", include("apps.users.api.urls")),
    path("api/core/", include("apps.core.api.urls")),
    path("api/audit/", include("apps.audit.urls")),
    path("api/produtos/", include("apps.produtos.api.urls")),
    path("api/estoque/", include("apps.estoque.api.urls")),
    path("api/fornecedores/", include("apps.fornecedores.api.urls")),
    path("api/compras/", include("apps.compras.api.urls")),
    path("api/recebimento/", include("apps.recebimento.api.urls")),
    # --------------------------------------------------------------
    # Proximos modulos serao plugados aqui nas proximas fases:
    # path("api/inventario/", include("apps.inventario.api.urls")),  # Modulo 6
    # path("api/relatorios/", include("apps.relatorios.api.urls")),  # Modulo 8
    # path("api/bi/", include("apps.bi.api.urls")),                  # Modulo 9
    # --------------------------------------------------------------
]
