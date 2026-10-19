from datetime import timedelta

from django.db.models import Count
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.employees.models import Department, Employee, EmploymentHistory
from apps.employees.serializers import (
    DepartmentSerializer,
    EmployeeSerializer,
    EmploymentHistorySerializer,
)


class DepartmentViewSet(TenantViewSet):
    queryset = Department.objects.select_related("manager")
    serializer_class = DepartmentSerializer
    required_permission = "employees.view"
    write_permission = "employees.manage"
    search_fields = ["code", "name"]
    filterset_fields = ["is_active"]


class EmployeeViewSet(TenantViewSet):
    queryset = Employee.objects.select_related("user", "department", "manager")
    serializer_class = EmployeeSerializer
    required_permission = "employees.view"
    write_permission = "employees.manage"
    search_fields = ["employee_no", "job_title", "user__first_name", "user__last_name", "user__email"]
    filterset_fields = ["status", "department"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        by_status = {label: qs.filter(status=value).count() for value, label in Employee.Status.choices}
        departments = (
            qs.filter(department__isnull=False)
            .values("department__name")
            .annotate(count=Count("id"))
            .order_by("-count")
        )
        recent_hires = qs.filter(hire_date__gte=timezone.now().date() - timedelta(days=31)).count()
        return Response(
            {
                "total": qs.count(),
                "active": by_status["active"],
                "on_leave": by_status["on_leave"],
                "terminated": by_status["terminated"],
                "departments": list(departments),
                "recent_hires": recent_hires,
            }
        )

    @action(detail=True, methods=["post"])
    def set_status(self, request, pk=None):
        employee = self.get_object()
        status = request.data.get("status")
        if status not in Employee.Status.values:
            return Response({"detail": f"Invalid status. Choose from {', '.join(Employee.Status.values)}"}, status=400)
        employee.status = status
        employee.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(employee).data)


class EmploymentHistoryViewSet(TenantViewSet):
    queryset = EmploymentHistory.objects.select_related("employee", "employee__user", "department")
    serializer_class = EmploymentHistorySerializer
    required_permission = "employees.view"
    write_permission = "employees.manage"
    search_fields = ["position", "employee__user__first_name", "employee__user__last_name"]
    filterset_fields = ["employee", "department"]
