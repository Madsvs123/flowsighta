from django.db.models import Q, Sum
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.core.mixins import TenantViewSet
from apps.crm.models import CrmActivity, Lead, Opportunity, Pipeline
from apps.crm.serializers import (
    CrmActivitySerializer,
    LeadSerializer,
    OpportunitySerializer,
    PipelineSerializer,
)


class LeadViewSet(TenantViewSet):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    required_permission = "crm.view"
    write_permission = "crm.manage"
    search_fields = ["name", "company", "email", "phone", "source"]
    filterset_fields = ["status", "source"]

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        leads_value = qs.aggregate(total_value=Sum("value")
        opps = Opportunity.objects.filter(organization=request.organization)
        opps_value = opps.aggregate(
            total=Sum("amount"), won=Sum("amount", filter=Q(status=Opportunity.Status.WON))
        )
        open_opps = opps.exclude(status=Opportunity.Status.OPEN)
        return Response(
            {
                "leads": qs.count(),
                "new_leads": qs.filter(status=Lead.Status.NEW).count(),
                "qualified_leads": qs.filter(status=Lead.Status.QUALIFIED).count(),
                "lost_leads": qs.filter(status=Lead.Status.LOST).count(),
                "lead_value": float(leads_value["total_value"] or 0),
                "opportunities": opps.count(),
                "open_opportunities": open_opps.count(),
                "won_opportunities": opps.filter(status=Opportunity.Status.WON).count(),
                "pipeline_value": float(opps_value["total"] or 0),
                "won_value": float(opps_value["won"] or 0),
                "stages": [
                    {"stage": stage, "count": open_opps.filter(stage=stage).count()}
                    for stage in open_opps.order_by().values_list("stage", flat=True).distinct()
                ],
            }
        )

    @action(detail=True, methods=["post"])
    def qualify(self, request, pk=None):
        lead = self.get_object()
        lead.status = Lead.Status.QUALIFIED
        lead.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(lead).data)

    @action(detail=True, methods=["post"])
    def lose(self, request, pk=None):
        lead = self.get_object()
        lead.status = Lead.Status.LOST
        lead.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(lead).data)


class OpportunityViewSet(TenantViewSet):
    queryset = Opportunity.objects.select_related("lead", "owner")
    serializer_class = OpportunitySerializer
    required_permission = "crm.view"
    write_permission = "crm.manage"
    search_fields = ["name", "lead__name", "stage"]
    filterset_fields = ["status", "stage", "owner", "lead"]

    @action(detail=True, methods=["post"])
    def win(self, request, pk=None):
        opportunity = self.get_object()
        opportunity.status = Opportunity.Status.WON
        opportunity.probability = 100
        opportunity.save(update_fields=["status", "probability", "updated_at"])
        return Response(self.get_serializer(opportunity).data)

    @action(detail=True, methods=["post"])
    def lose(self, request, pk=None):
        opportunity = self.get_object()
        opportunity.status = Opportunity.Status.LOST
        opportunity.save(update_fields=["status", "updated_at"])
        return Response(self.get_serializer(opportunity).data)


class CrmActivityViewSet(TenantViewSet):
    queryset = CrmActivity.objects.select_related("opportunity", "lead")
    serializer_class = CrmActivitySerializer
    required_permission = "crm.view"
    write_permission = "crm.manage"
    search_fields = ["notes", "opportunity__name", "lead__name"]
    filterset_fields = ["type", "opportunity", "lead"]


class PipelineViewSet(TenantViewSet):
    queryset = Pipeline.objects.all()
    serializer_class = PipelineSerializer
    required_permission = "crm.view"
    write_permission = "crm.manage"
    search_fields = ["name"]
    filterset_fields = ["is_default", "is_active"]
