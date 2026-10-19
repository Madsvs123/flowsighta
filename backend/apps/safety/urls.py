from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.safety.views import (
    IncidentInvestigationViewSet,
    IncidentViewSet,
    SafetyInspectionViewSet,
    SafetyTrainingViewSet,
)

router = DefaultRouter()
router.register("incidents", IncidentViewSet, basename="incident")
router.register("investigations", IncidentInvestigationViewSet, basename="incidentinvestigation")
router.register("inspections", SafetyInspectionViewSet, basename="safetyinspection")
router.register("trainings", SafetyTrainingViewSet, basename="safety_training")

urlpatterns = [
    path("safety/", include(router.urls)),
]
