from rest_framework.routers import DefaultRouter

from apps.tickets.views import (
    SupportTicketViewSet,
    TicketCategoryViewSet,
    TicketMessageViewSet,
    TicketSlaViewSet,
)

router = DefaultRouter()
router.register("tickets", SupportTicketViewSet, basename="tickets")
router.register("ticket-categories", TicketCategoryViewSet, basename="ticket-categories")
router.register("ticket-message", TicketMessageViewSet, basename="ticket-messages")
router.register("ticket-slas", TicketSlaViewSet, basename="ticket-slas")

urlpatterns = router.urls
