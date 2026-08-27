from rest_framework.routers import DefaultRouter

from .views import CategoriaViewSet, FabricanteViewSet, ProdutoViewSet

router = DefaultRouter()
router.register("produtos", ProdutoViewSet, basename="produto")
router.register("categorias", CategoriaViewSet, basename="categoria")
router.register("fabricantes", FabricanteViewSet, basename="fabricante")

urlpatterns = router.urls
