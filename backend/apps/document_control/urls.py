from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.document_control.views import (
    DocumentApprovalViewSet,
    DocumentLinkViewSet,
    DocumentRevisionViewSet,
    DocumentViewSet,
)

router = DefaultRouter()
router.register("documents", DocumentViewSet, basename="document")
router.register("revisions", DocumentRevisionViewSet, basename="documentrevision")
router.register("approvals", DocumentApprovalViewSet, basename="documentapproval")
router.register("links", DocumentLinkViewSet, basename="documentlink")

urlpatterns = [
    path("document-control", include(router.urls)),
]
