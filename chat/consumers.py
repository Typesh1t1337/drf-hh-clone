from datetime import timezone

from asgiref.sync import sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from .models import *
from .tasks import celery_message_to_support
# class ChatSupportConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.chat_id = self.scope['url_route']['kwargs']['chat_id']
#         self.room_group_name = f"chat_{self.chat_id}"
#
#
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#
#     async def receive(self, text_data=None, bytes_data=None):
#         text_data_json = json.loads(text_data)
#
#         message = text_data_json['message']
#         username = text_data_json['username']
#         first_name = text_data_json['first_name']
#
#         task = celery_message_to_support.apply_async(kwargs={"text": message,
#                                                              "username": username,
#                                                              "chat_id": self.chat_id,
#                                                              "first_name": first_name})
#
#
#         await self.update_chat(chat_id=self.chat_id, text=message)
#
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'sender': username,
#                 'first_name': first_name,
#             }
#         )
#
#     async def chat_message(self, event):
#         message = event['message']
#         username = event['username']
#         first_name = event['first_name']
#
#
#         await self.send(text_data=json.dumps({
#             'message': message,
#             'sender': username,
#             'is_read': False,
#             'message_date': timezone.now().isoformat()
#         }))
#
#     @sync_to_async()
#     def update_chat(self,chat_id, text):
#         chat = Chat.objects.get(id=chat_id)
#         chat.last_message = text
#         chat.save(update_fields=['last_message'])
#
#
#     def get_message_data(self,sender,message):
#


class ChatConsumer(AsyncWebsocketConsumer):
    pass