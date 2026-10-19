from rest_framework.routers import DefaultRouter

from apps.recruiting.views import (
    ApplicationViewSet,
    CandidateViewSet,
    InterviewViewSet,
    JobPostingViewSet,
    OfferViewSet,
)

router = DefaultRouter()
router.register("recruiting", JobPostingViewSet, basename="jobposting")
router.register("candidates", CandidateViewSet, basename="candidate")
router.register("application", ApplicationViewSet, basename="application")
router.register("interviews", InterviewViewSet, basename="interview")
router.register("offers", OfferViewSet, basename="offer")

urlpatterns = router.urls
