from django.contrib import admin

from apps.document_control.models import (
    Document,
    DocumentApproval,
    DocumentLink,
    DocumentRevision,
)


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "type", "status", "owner")
    list_filter = ("type",)
    search_fields = ("code", "title")


@admin.register(DocumentRevision)
class DocumentRevisionAdmin(admin.ModelAdmin):
    list_display = ("document", "version", "approved_by", "approved_at")
    list_filter = ("approved_at",)


@admin.register(DocumentApproval)
class DocumentApprovalAdmin(admin.ModelAdmin):
    list_display = ("revision", "approver", "decision", "comment")
    list_filter = ("decision",)
    search_fields = ("approver__email", "revision__document__code")


@admin.register(DocumentLink)
class DocumentLinkAdmin(admin.ModelAdmin):
    list_display = ("document", "object_type", "object_id")
    list_filter = ("object_type",)
    search_fields = ("document__code", "object_id")
