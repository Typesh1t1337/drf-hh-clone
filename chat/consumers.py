from django.utils import timezone

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import *
from .tasks import celery_chat


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope['url_route']['kwargs']['chat_id']
        self.room_group_name = f"chat_{self.chat_id}"


        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )


    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)

        message = text_data_json['message']
        sender = text_data_json['sender']
        receiver = text_data_json['receiver']



        celery_chat.apply_async(args=[sender, receiver, message, self.chat_id])

        await self.update_chat(chat_id=self.chat_id, text=message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'sender': sender,
                'receiver': receiver,
            }
        )

    async def chat_message(self, event):
        message = event['message']
        sender = event['sender']
        receiver = event['receiver']



        await self.send(text_data=json.dumps({
            'message': message,
            'sender': sender,
            'receiver': receiver,
            'message_date': timezone.now().isoformat(),
            'is_read' : False
        }))

    @sync_to_async()
    def update_chat(self,chat_id, text):
        chat = Chat.objects.filter(id=chat_id).first()
        if chat:
            chat.last_message = text
            chat.save(update_fields=['last_message'])



