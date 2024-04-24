import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import User
from asgiref.sync import sync_to_async
from .models import Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        if self.scope['user'].is_authenticated:
            print("---------> Connected to WebSocket")
            await self.accept()  # Accept the WebSocket connection
        else:
            print("---------> Connection rejected: User is not authenticated.")
            await self.close()  # Reject the WebSocket connection


    async def disconnect(self, close_code):
        print("---------> Disconnected from WebSocket")


    async def receive(self, text_data):
        print("---------> Received message from WebSocket:", text_data)

        try:
            message_data = json.loads(text_data)
            content = message_data.get('content')

            if content:
                # Fetch the sender's user object from the database using the authenticated user ID
                sender_id = self.scope['user'].id
                print("------------------senderId--------------------------")
                print(sender_id)
                print("--------------------------------------------")
                sender = await self.get_user_by_id(sender_id)

                # Get the receiver ID from the URL path
                receiver_id = self.scope['url_route']['kwargs']['receiver_id']
                receiver = await self.get_user_by_id(receiver_id)

                # Save the message to the database
                await self.save_message(sender, receiver, content)

                print("Message saved to the database.")

                # send me back the message for the textearea
                await self.send(text_data=json.dumps({
                    'message': content
                }))
               
            else:
                print("Received message is empty or does not contain content.")
        except json.JSONDecodeError:
            print("Failed to parse received message as JSON.")

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
