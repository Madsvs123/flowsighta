from django.contrib import admin

from apps.feedback.models import Complaint, FeedbackResponse, FeedbackSurvey, NpsScore

admin.site.register(FeedbackSurvey)
admin.site.register(FeedbackResponse)
admin.site.register(NpsScore)
