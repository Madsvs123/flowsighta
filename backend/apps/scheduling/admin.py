from django.contrib import admin

from apps.scheduling.models import Schedule, ScheduleConstraint, ScheduleTask

admin.site.register(Schedule)
admin.site.register(ScheduleTask)
admin.site.register(ScheduleConstraint)
