from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.picking.views import PickLineViewSet, PickTaskViewSet, PickWaveViewSet

router = DefaultRouter()
router.register("waves", PickWaveViewSet, basename="pickwaves")
router.register("pick-lines", PickLineViewSet, basename="picklines")
router.register("pick-tasks", PickLineViewSet, basename="picktasks")

urlpatterns = [
    path("picking/", include(router.urls)),
]
