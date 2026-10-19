from django.contrib import admin

from apps.recruiting.models import Application, Candidate, Interview, JobPosting, Offer


@admin.register(JobPosting)
class JobPostingAdmin(admin.ModelAdmin):
    list_display = ("title", "department", "status", "openings", "salary_range")
    list_filter = ("status", "department")


@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "phone", "source", "status")
    list_filter = ("status", "source")
    search_fields = ("name", "email")


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("candidate", "posting", "status", "applied_at")
    list_filter = ("status", "posting")
    search_fields = ("candidate__name", "candidate_email")


@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ("application", "interviewer", "date", "score")
    list_filter = ("interviewer",)


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("application", "salary", "status", "expires_at")
    list_filter = ("status",)
