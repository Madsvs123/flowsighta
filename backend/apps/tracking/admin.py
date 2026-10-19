from django.contrib import admin

from apps.tracking.models import EtaPrediction, GeofenceEvent, GeoFence, TrackingEvent

admin.site.register(TrackingEvent)
admin.site.register(GeoFence)
admin.site.register(GeofenceEvent)
admin.site.register(EtaPrediction)
