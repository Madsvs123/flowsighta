from rest_framework.routers import DefaultRouter

from apps.bills_of_materials.views import BomLineViewSet, BomRevisionViewSet, BomViewSet

router = DefaultRouter()
router.register("bills-of-materials", BomViewSet, basename="boms")
router.register("bills-of-materials/lines", BomLineViewSet, basename="bom-lines")
router.register("bills-of-materials/revisions", BomLineViewSet, basename="bom-revisions")

urlpatterns = router.urls
