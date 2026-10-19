from rest_framework import serializers

from apps.core.mixins import TenantSerializer
from apps.scheduling.models import Schedule, ScheduleConstraint, ScheduleTask


class ScheduleSerializer(TenantSerializer):
    task_count = serializers.SerializerMethodField()

    class Meta:
        model = Schedule
        fields = (
            "id",
            "name",
            "horizon_start",
            "horizon_end",
            "status",
            "task_count",
            "created_at",
        )
        read_only_fields = ("id", "created_at")

    def get_task_count(self, obj):
        return obj.tasks.count()


class ScheduleTaskSerializer(TenantSerializer):
    schedule_name = serializers.CharField(source="schedule.name", read_only=True)

    class Meta:
        model = ScheduleTask
        fields = (
            "id",
            "schedule",
            "schedule_name",
            "reference",
            "resource",
            "start_at",
            "end_at",
            "status",
            "created_at",
        )
        read_only_fields = ("id", "created_at")


class ScheduleConstraintSerializer(TenantSerializer):
    task_reference = serializers.CharField(source="task.reference", read_only=True)

    class Meta:
        model = ScheduleConstraint
        fields = (
            "id",
            "task",
            "task_reference",
            "type",
            "value",
            "created_at",
        )
        read_only_fields = ("id", "created_at"
