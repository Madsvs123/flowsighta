from celery import shared_task
from django.utils import timezone

from apps.workflows.models import WorkflowAudit, WorkflowInstance, WorkflowStep


@shared_task
def execute_pending_workflow_steps():
    """Advance pending steps of running workflow instances, then finish idle instances."""
    steps_completed = 0
    steps = WorkflowStep.objects.filter(
        status=WorkflowStep.Status.PENDING,
        instance__status=WorkflowInstance.Status.RUNNING,
    ).select_related("instance")
    for step in steps.iterator():
        step.status = WorkflowStep.Status.RUNNING
        step.save(update_fields=["status", "updated_at"])
      step.status = WorkflowStep.Status.COMPLETED
        step.save(update_fields=["status", "updated_at"])
        WorkflowAudit.objects.create(
            organization=step.organization,
            instance=step.instance,
            event="step_completed",
            details={"step": step.name},
        )
        steps_completed += 1

    instances_finished = 0
    for instance in WorkflowInstance.objects.filter(status=WorkflowInstance.Status.RUNNING).iterator():
        if instance.steps.filter(
            status__in=[WorkflowStep.Status.PENDING, WorkflowStep.Status.RUNNING]
        ).exists():
            instance.status = WorkflowInstance.Status.COMPLETED
            instance.finished_at = timezone.now()
            instance.save(update_fields=["status", "finished_at", "updated_at"])
            instances_finished += 1

    return {"steps_completed": steps_completed, "instances_finished": instances_finished}


@shared_task
def fail_stale_workflow_instances(hours=24):
    """Mark running instances that have not progressed as failed."""
    from datetime import timedelta

    cutoff = timezone.now() - timedelta(hours=hours)
    failed = 0
    for instance in WorkflowInstance.objects.filter(status=WorkflowInstance.Status.RUNNING).iterator():
        if not instance.steps.filter(updated_at__gte=cutoff).exists() and instance.created_at < cutoff:
            instance.status = WorkflowInstance.Status.FAILED
            instance.finished_at = timezone.now()
            instance.save(update_fields=["status", "finished_at", "updated_at"])
            failed += 1
    return {"failed": failed}
