from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AjusteEstoqueView,
    BaixaEstoqueView,
    EntradaEstoqueView,
    LoteViewSet,
    MovimentoEstoqueViewSet,
    ProdutosVencendoView,
    SaidaEstoqueView,
    TransferenciaEstoqueView,
)

router = DefaultRouter()
router.register("lotes", LoteViewSet, basename="lote")
router.register("movimentos", MovimentoEstoqueViewSet, basename="movimento")

urlpatterns = [
    path("entrada/", EntradaEstoqueView.as_view(), name="estoque-entrada"),
    path("saida/", SaidaEstoqueView.as_view(), name="estoque-saida"),
    path("baixa/", BaixaEstoqueView.as_view(), name="estoque-baixa"),
    path("transferencia/", TransferenciaEstoqueView.as_view(), name="estoque-transferencia"),
    path("ajuste/", AjusteEstoqueView.as_view(), name="estoque-ajuste"),
    path("vencendo/", ProdutosVencendoView.as_view(), name="estoque-vencendo"),
] + router.urls
