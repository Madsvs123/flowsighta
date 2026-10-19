from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.contracts.views import (
    ContractClauseViewSet,
    ContractMilestoneViewSet,
    ContractViewSet,
)

router = DefaultRouter()
router.register("contracts", ContractViewSet, basename="contract"
router.register("clauses", ContractClauseViewSet, basename="contract-clause")
router.register("milestones", ContractMilestoneViewSet, basename="contract-milestone")

urlpatterns = [
    path("contracts/", include(router.urls)),
]
