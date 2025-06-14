# import json
# from channels.generic.websocket import AsyncWebsocketConsumer
# from channels.db import database_sync_to_async
# from django.contrib.auth.models import User
# from .models import GroupChat, StudyGroup
#
# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.group_id = self.scope['url_route']['kwargs']['group_id']
#         self.room_group_name = f'chat_{self.group_id}'
#
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#
#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )
#
#     async def receive(self, text_data):
#         data = json.loads(text_data)
#         message = data['message']
#         username = data['username']
#
#         await self.save_message(username, message)
#
#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': message,
#                 'username': username
#             }
#         )
#
#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'username': event['username'],
#         }))
#
#     @database_sync_to_async
#     def save_message(self, username, content):
#         user = User.objects.get(username=username)
#         group = StudyGroup.objects.get(id=self.group_id)
#         return GroupChat.objects.create(user=user, group=group, content=content)
