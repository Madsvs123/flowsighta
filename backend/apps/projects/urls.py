from rest_framework.routers import DefaultRouter

from apps.projects.views import (
    ProjectMemberViewSet,
    ProjectMilestoneViewSet,
    ProjectTaskViewSet,
    ProjectViewSet,
)

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="projects")
router.register("project-members", ProjectMemberViewSet, basename="projectmember")
router.register("project-tasks", ProjectTaskViewSet, basename="projecttask")
router.register("project-milestones", ProjectMilestoneViewSet, basename="projectmilestone")

urlpatterns = router.urls
