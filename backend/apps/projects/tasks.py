from celery import shared_task
from django.db.models import Q
from django.utils import timezone

from apps.projects.models import ProjectMilestone, ProjectTask


@shared_task
def flag_overdue_project_items():
    """Flag milestones past their due date as slipped and overdue open tasks as blocked."""
    today = timezone.now().date()
    slipped = ProjectMilestone.objects.filter(
        status=ProjectMilestone.Status.PENDING, date__lte=today
    ).update(status=ProjectMilestone.Status.SLIPPED)
    blocked = ProjectTask.objects.filter(
        Q(status__in=[ProjectTask.Status.TODO, ProjectTask.Status.IN_PROGRESS]),
        due_date__lt=today,
    ).update(status=ProjectTask.Status.BLOCKED)
    return {"milestones_slipped": slipped, "tasks_blocked": blocked}
