from rest_framework.routers import DefaultRouter
from django.urls import path

from .views import LoginView, MeView, PerfisDisponiveisView, RefreshView, UserViewSet

router = DefaultRouter()
router.register("usuarios", UserViewSet, basename="usuario")

urlpatterns = [
    path("login/", LoginView.as_view(), name="login"),
    path("refresh/", RefreshView.as_view(), name="refresh"),
    path("me/", MeView.as_view(), name="me"),
    path("perfis/", PerfisDisponiveisView.as_view(), name="perfis-disponiveis"),
] + router.urls
