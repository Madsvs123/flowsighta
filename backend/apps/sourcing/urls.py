from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.sourcing.views import (
    SourcingAwardViewSet,
    SourcingBidViewSet,
    SourcingEventViewSet,
    SourcingLineViewSet,
)

router = DefaultRouter()
router.register("events", SourcingEventViewSet, basename="sourcing-event")
router.register("lines", SourcingLineViewSet, basename="sourcing-event")
router.register("bids", SourcingBidViewSet, basename="sourcing-bid")
router.register("awards", SourcingAwardViewSet, basename="sourcing-award")

urlpatterns = [
    path("sourcing/", include(router.urls)),
]
