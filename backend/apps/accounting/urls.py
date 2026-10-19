from rest_framework.routers import DefaultRouter

from apps.accounting.views import (
    AccountingPeriodViewSet,
    AccountViewSet,
    JournalEntryViewSet,
    JournalLineViewSet,
)

router = DefaultRouter()
router.register("accounts", AccountViewSet, basename="accounts")
router.register("journal-entries", JournalEntryViewSet, basename="journal-entry")
router.register("journal-lines", JournalLineViewSet, basename="journal-lines")
router.register("accounting-periods", AccountingPeriodViewSet, basename="accounting-periods")

urlpatterns = router.urls
