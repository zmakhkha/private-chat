from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message
import json
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            print("---------> Connected to WebSocket")
            await self.accept()
            sender_id = self.scope['user'].id
            print("---------> User n°:", sender_id, " connected !")
            receiver_id = self.scope['url_route']['kwargs']['receiver_id']
            group_name = self.get_group_name(sender_id, receiver_id)
            print("---------> Group n°:", group_name, " created !")
            await self.channel_layer.group_add(group_name, self.channel_name)
            print("---------> Channel name : ", self.channel_name)
            
        else:
            print("---------> Connection rejected: User is not authenticated.")
            await self.close()

    async def disconnect(self, close_code):
        print("---------> Disconnected from WebSocket")
        sender_id = self.scope['user'].id
        receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        group_name = self.get_group_name(sender_id, receiver_id)
        await self.channel_layer.group_discard(group_name, self.channel_name)

    async def receive(self, text_data):
        print("---------> Received message from WebSocket:", text_data)

        try:
            message_data = json.loads(text_data)
            content = message_data.get('content')

            if content:
                sender_id = self.scope['user'].id
                receiver_id = self.scope['url_route']['kwargs']['receiver_id']
                receiver = await self.get_user_by_id(receiver_id)
                sender = await self.get_user_by_id(sender_id)
                
                group_name = self.get_group_name(sender_id, receiver_id)
                await self.save_message(sender, receiver, content)
                # Broadcast the message to the group
                x = datetime.datetime.now()
                await self.channel_layer.group_send(
                    group_name,
                    {
                        'type': 'chat_message',
                        'user' : self.scope['user'].username,
                        'timestamp' : {
                            'year' : x.year,
                            'month' : x.month,
                            'day' : x.day,
                            'hour' : x.hour,
                            'minute' : x.minute,
                        },
                        'content': content
                    }
                )
            else:
                print("Received message is empty or does not contain content.")
        except json.JSONDecodeError:
            print("Failed to parse received message as JSON.")

    async def chat_message(self, event):
        content = event['content']
        sender = event['user']
        timestamp = event['timestamp']

        # Send the message to the WebSocket
        await self.send(text_data=json.dumps({
            'user' : sender,
            'timestamp' : timestamp,
            'message': content
        }))

    def get_group_name(self, user_id1, user_id2):
        # Ensure consistent group naming regardless of sender/receiver order
        if user_id1 is not None and user_id2 is not None:
            return f"group_{min(user_id1, user_id2)}_{max(user_id1, user_id2)}"
        else:
            # Handle the case where one of the user IDs is None
            return None

    @sync_to_async
    def get_user_by_id(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            print("--------------------------------------------")
            print(user_id)
            print("--------------------------------------------")
            print("User does not exist with ID:", user_id)
            return None

    @sync_to_async
    def save_message(self, sender, receiver, content):
        if sender and receiver:
            message = Message.objects.create(sender=sender, receiver=receiver, content=content)
            message.save()