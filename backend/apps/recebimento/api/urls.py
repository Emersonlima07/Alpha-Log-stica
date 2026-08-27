from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AprovarRecebimentoView,
    ConferirItemView,
    ImportarXmlNfeView,
    IniciarRecebimentoView,
    RecebimentoViewSet,
    RejeitarRecebimentoView,
)

router = DefaultRouter()
router.register("recebimentos", RecebimentoViewSet, basename="recebimento")

urlpatterns = [
    path("iniciar/", IniciarRecebimentoView.as_view(), name="recebimento-iniciar"),
    path("importar-xml/", ImportarXmlNfeView.as_view(), name="recebimento-importar-xml"),
    path("itens/<int:item_id>/conferir/", ConferirItemView.as_view(), name="recebimento-conferir-item"),
    path("<int:recebimento_id>/aprovar/", AprovarRecebimentoView.as_view(), name="recebimento-aprovar"),
    path("<int:recebimento_id>/rejeitar/", RejeitarRecebimentoView.as_view(), name="recebimento-rejeitar"),
] + router.urls
