from rest_framework.routers import DefaultRouter

from apps.feedback.views import (
    ComplaintViewSet,
    FeedbackResponseViewSet,
    FeedbackSurveyViewSet,
    NpsScoreViewSet,
)

router = DefaultRouter()
router.register("surveys", FeedbackSurveyViewSet, basename="surveys")
router.register("responses", FeedbackResponseViewSet, basename="responses")
router.register("nps-scores", NpsScoreViewSet, basename="nps-scores")
router.register("complaints", ComplaintViewSet, basename="complaint")

urlpatterns = router.urls
