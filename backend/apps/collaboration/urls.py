from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.collaboration.views import (
    ActivityViewSet,
    AuditLogViewSet,
    CommentViewSet,
    DocumentViewSet,
    NotificationViewSet,
    SavedFilterViewSet,
    TaskViewSet,
    global_search,
)

router = DefaultRouter()
router.register("comments", CommentViewSet, basename="comments"
router.register("notifications", NotificationViewSet, basename="notifications")
router.register("activity", ActivityViewSet, basename="activities")
router.register("documents", DocumentViewSet, basename="documents")
router.register("tasks", TaskViewSet, basename="tasks")
router.register("saved-filters", SavedFilterViewSet, basename="saved-filters")
router.register("audit-logs", AuditLogViewSet, basename="audit-logs")

urlpatterns = [path("search/", global_search, name="global-search")] + router.urls

