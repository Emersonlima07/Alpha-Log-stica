from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AdicionarCotacaoView,
    AprovarSolicitacaoView,
    CancelarPedidoView,
    CriarSolicitacaoView,
    EnviarPedidoView,
    PedidoCompraViewSet,
    RejeitarSolicitacaoView,
    SelecionarCotacaoView,
    SolicitacaoCompraViewSet,
)

router = DefaultRouter()
router.register("solicitacoes", SolicitacaoCompraViewSet, basename="solicitacao-compra")
router.register("pedidos", PedidoCompraViewSet, basename="pedido-compra")

urlpatterns = [
    path("solicitacoes/nova/", CriarSolicitacaoView.as_view(), name="compras-nova-solicitacao"),
    path("solicitacoes/<int:solicitacao_id>/cotacoes/", AdicionarCotacaoView.as_view(), name="compras-adicionar-cotacao"),
    path("cotacoes/<int:cotacao_id>/selecionar/", SelecionarCotacaoView.as_view(), name="compras-selecionar-cotacao"),
    path("solicitacoes/<int:solicitacao_id>/aprovar/", AprovarSolicitacaoView.as_view(), name="compras-aprovar-solicitacao"),
    path("solicitacoes/<int:solicitacao_id>/rejeitar/", RejeitarSolicitacaoView.as_view(), name="compras-rejeitar-solicitacao"),
    path("pedidos/<int:pedido_id>/enviar/", EnviarPedidoView.as_view(), name="compras-enviar-pedido"),
    path("pedidos/<int:pedido_id>/cancelar/", CancelarPedidoView.as_view(), name="compras-cancelar-pedido"),
] + router.urls
