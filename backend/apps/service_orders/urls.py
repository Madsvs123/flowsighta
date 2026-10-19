from rest_framework.routers import DefaultRouter

from apps.service_orders.views import (
    FieldReportViewSet,
    ServiceAppointmentViewSet,
    ServiceLineViewSet,
    ServiceOrderViewSet,
)

router = DefaultRouter()
router.register("service-orders", ServiceOrderViewSet, basename="service-orders")
router.register("service-lines", ServiceLineViewSet, basename="service-line")
router.register("service-appointments", ServiceAppointmentViewSet, basename="service-appointments")
router.register("field-reports", FieldReportViewSet, basename="field-reports")

urlpatterns = router.urls
