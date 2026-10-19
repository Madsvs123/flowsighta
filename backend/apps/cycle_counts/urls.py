from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.cycle_counts.views import CountLineViewSet, CycleCountViewSet

router = DefaultRouter()
router.register("cycle-counts", CycleCountViewSet, basename="cyclecounts")
router.register("count-lines", CountLineViewSet, basename="countlines")

urlpatterns = [
    path("cycle-counts", include(router.urls)),
]
