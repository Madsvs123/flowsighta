from django.contrib import admin

from apps.approvals.models import ApprovalDecision, ApprovalPolicy, ApprovalRequest, ApprovalStep


@admin.register(ApprovalPolicy)
class ApprovalPolicyAdmin(admin.ModelAdmin):
    list_display = ("name", "object_type", "threshold", "is_active")
    list_filter = ("object_type", "is_active")
    search_fields = ("name", "type")


@admin.register(ApprovalRequest)
class ApprovalRequestAdmin(admin.ModelAdmin):
    list_display = ("reference", "policy", "status", "requested_by", "requested_at")
    list_filter = ("status",)
    search_fields = ("reference", "object_id")


@admin.register(ApprovalStep)
class ApprovalStepAdmin(admin.ModelAdmin):
    list_display = ("request", "sequence", "approver", "status")
    list_filter = ("status",)


@admin.register(ApprovalDecision)
class ApprovalDecisionAdmin(admin.ModelAdmin):
    list_display = ("step", "decision", "decided_at")
    list_filter = ("decision",)
