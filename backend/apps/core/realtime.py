from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


def publish_organization_event(organization_id, event_type, payload)
    channel_layer = get_channel_layer()
    if channel_layer is None:
        return
    async_to_sync(channel_layer.group_send)(
        f"org_{organization_id}",
        {
            "type": "realtime.event",
            "payload": {"type": event_type, "data": payload},
        },
    )
