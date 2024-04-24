from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.http import HttpResponse
from django.views import View
from .models import Message

@login_required
def chat_view(request, receiver_id):
    # Fetch messages for the current user and the specified receiver
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(sender=request.user, receiver=receiver) | Message.objects.filter(sender=receiver, receiver=request.user)
    # Include sender's name along with messages
    messages_with_sender_name = []
    for message in messages:
        if message.sender == request.user:
            sender_name = "You"
        else:
            sender_name = message.sender.username
        messages_with_sender_name.append((sender_name, message.content))
    return render(request, 'chat/chat.html', {'messages': messages_with_sender_name, 'receiver_id': receiver_id})

@login_required
def send_message(request, receiver_id):
    if request.method == 'POST':
        content = request.POST.get('content')
        
        if content:
            try:
                receiver = User.objects.get(id=receiver_id)
                Message.objects.create(sender=request.user, receiver=receiver, content=content)
                return redirect('chat', receiver_id=receiver_id)  # Redirect back to chat view
            except User.DoesNotExist:
                return HttpResponse("Receiver not found", status=400)
        else:
            return HttpResponse("Invalid request", status=400)
    else:
        return HttpResponse("Method not allowed", status=405)


class MessageListView(View):
    def get(self, request, sender_id, receiver_id):
        # Ensure the current user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Ensure the current user is one of the specified sender or receiver
        if request.user.id != sender_id and request.user.id != receiver_id:
            return JsonResponse({'error': 'You are not authorized to access these messages'}, status=403)

        # Retrieve messages between the specified sender and receiver
        messages = Message.objects.filter(
            sender_id=sender_id,
            receiver_id=receiver_id
        ).values('id', 'sender__username', 'receiver__username', 'content', 'timestamp')

        return JsonResponse(list(messages), safe=False)