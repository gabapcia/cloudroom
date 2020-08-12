from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.auth import AnonymousUser, get_user


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def user_is_authenticated(self):
        user = await get_user(self.scope)
        return user.is_authenticated

    async def connect(self):
        self.room_group_name = 'chris'

        if await self.user_is_authenticated():
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code=1001):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, data):
        if await self.user_is_authenticated():
            message = data['message']

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message
                }
            )
        else: self.disconnect()

    async def chat_message(self, event):
        message = event['message']
        await self.send_json(content={'message': message})
