from rest_framework.routers import DefaultRouter

from ..views import EmpresaViewSet, FilialViewSet

router = DefaultRouter()
router.register("empresas", EmpresaViewSet, basename="empresa")
router.register("filiais", FilialViewSet, basename="filial")

urlpatterns = router.urls
