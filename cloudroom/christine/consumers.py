from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.auth import get_user
from channels.db import database_sync_to_async
from .engine import Engine
from .models import ChristineResponse, Message


class ChatConsumer(AsyncJsonWebsocketConsumer):
    async def user_is_authenticated(self):
        user = await get_user(self.scope)
        return user.is_authenticated

    async def connect(self):
        self.room_group_name = 'chris'
        self.stage = None
        self.engine = None

        if await self.user_is_authenticated():
            self.engine = Engine()
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code=1001):
        del self.engine
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive_json(self, data):
        if await self.user_is_authenticated():
            message = data['message']

            await self.__handle_message(message=message)
            await self.__process_message(message=message)
        else: self.disconnect()

    async def chat_message(self, event):
        await self.send_json(content={
            'message': event['message'],
            'from_chris': event['from_chris']
        })

    async def __send_group_message(self, message, from_chris=False):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'from_chris': from_chris,
            }
        )

    async def __process_message(self, message):
        try:
            if not self.stage:
                self.stage = self.engine.process(text=message)
                data = next(self.stage)
            else: data = self.stage.send(message)
            if 'result' in data: 
                self.stage = None
                data = data['result']
            else: data = data['request']
            await self.__handle_message(
                message=data.get('speak', 'Done!'), 
                from_chris=True,
                type=(
                    ChristineResponse.CommandType.REQUEST 
                    if self.stage 
                    else ChristineResponse.CommandType.RESULT
                ),
                **data
            )
        except Exception as e:
            response = f'Sorry, an error has occured: {e}'
            self.stage = None
            await self.__handle_message(
                message=response, 
                from_chris=True,
                type=ChristineResponse.CommandType.ERROR
            )

    async def __handle_message(self, from_chris=False, **data):
        await self.__persist_message(
            from_chris=from_chris,
            user=await get_user(self.scope),
            **data
        )
        await self.__send_group_message(
            message=data['message'], 
            from_chris=from_chris,
        )

    @database_sync_to_async
    def __persist_message(self, from_chris, user, **data):
        if from_chris:
            ChristineResponse.objects.create(
                text=data['message'], 
                message=self.last_message,
                command_type=data.pop('type'),
                content=data,
            )
        else:
            self.last_message = Message.objects.create(
                text=data['message'],
                sender=user
            )
