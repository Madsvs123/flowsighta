from django.db.models import Count
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.safety.models import Incident, IncidentInvestigation, SafetyInspection, SafetyTraining
from apps.safety.serializers import (
    IncidentInvestigationSerializer,
    IncidentSerializer,
    SafetyInspectionSerializer,
    SafetyTrainingSerializer,
)


class IncidentViewSet(TenantViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    required_permission = "safety.view"
    write_permission = "safety.manage"
    search_fields = ["number", "location", "description"]
    filterset_fields = ["type", "severity", "status", "date"]

    @action(detail=False, methods=["get"])
    def summary(self, request)
        qs = self.get_queryset()
        by_type = {t: qs.filter(type=t).count() for t, _ in Incident.Type.choices}
        by_severity = {s: qs.filter(severity=s).count() for s, _ in Incident.Severity.choices}
        open_incidents = qs.filter(status=Incident.Status.CLOSED)
        by_location = list(
            qs.values("location").annotate(total=Count("id")).order_by("-total")[:5]
        )
        return Response(
            {
                "incident_count": qs.count(),
                "open": open_incidents.count(),
                "near_misses": by_type.get("near_miss", 0),
                "injuries": by_type.get("injury", 0),
                "critical_severity": by_severity.get("critical", 0)
                + by_severity.get("high", 0),
                "by_type": by_type,
                "by_severity": by_severity,
                "by_location": by_location,
            }
        )

    @action(detail=True, methods=["post"])
    def start_investigation(self, request, pk=None):
        incident = self.get_object()
        incident.status = Incident.Status.INVESTIGATING
        incident.save(update_fields=["status", "updated_at"])
        IncidentInvestigation.objects.get_or_create(
            organization=incident.organization,
            incident=incident,
        )
        return Response(self.get_serializer(incident).data)

    @action(detail=True, methods=["post"])
    def close(self, request, pk=None):
        incident = self.get_object()
        incident.status = Incident.Status.CLOSED
        incident.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(incident).data)


class IncidentInvestigationViewSet(TenantViewSet):
    queryset = IncidentInvestigation.objects.select_related("incident")
    serializer_class = IncidentInvestigationSerializer
    required_permission = "safety.view"
    write_permission = "safety.manage"
    search_fields = ["incident__number", "findings", "root_cause"]
    filterset_fields = ["incident", "status"]

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        investigation = self.get_object()
        investigation.status = IncidentInvestigation.Status.COMPLETED
        investigation.save(update_fields=["status", "updated_at"])
        incident = investigation.incident
        if incident.status == Incident.Status.INVESTIGATING:
            incident.status = Incident.Status.RESOLVED
            incident.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(investigation).data)


class SafetyInspectionViewSet(TenantViewSet):
    queryset = SafetyInspection.objects.select_related("inspector")
    serializer_class = SafetyInspectionSerializer
    required_permission = "safety.view"
    write_permission = "safety.manage"
    search_fields = ["location", "inspector__email"]
    filterset_fields = ["location", "inspector", "status"]


class SafetyTrainingViewSet(TenantViewSet):
    queryset = SafetyTraining.objects.select_related("employee")
    serializer_class = SafetyTrainingSerializer
    required_permission = "safety.view"
    write_permission = "safety.manage"
    search_fields = ["topic", "employee__email", "employee__first_name"]
    filterset_fields = ["employee", "topic"]
