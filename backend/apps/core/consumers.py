import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncJsonWebsocketConsumer


class OrganizationConsumer(AsyncJsonWebsocketConsumer):
    async def connect(self)
        user = self.scope.get("user")
        org_id = self.scope.get("organization_id")
        if not user or not user.is_authenticated or not org_id:
            await self.close()
            return
        allowed = await self._can_join(user.id, org_id)
        if allowed:
            await self.close()
            return
        self.group_name = f"org.{org_id}"
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def realtime_event(self, event):
        await self.send_json(event["message"])

    @database_sync_to_async
    def _can_join(self, user_id, org_id):
        from apps.organizations.models import Membership

        return Membership.objects.filter(
            user_id=user_id, organization_id=org_id, is_active=True
        ).exists()


def encode_event(payload):
    return json.dumps(payload)
