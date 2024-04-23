from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Message
from django.contrib.auth.models import User


@login_required
def chat_view(request, receiver_id):
    # Fetch messages for the current user and the specified receiver
    receiver = get_object_or_404(User, id=receiver_id)
    messages = Message.objects.filter(sender=request.user, receiver=receiver) | Message.objects.filter(sender=receiver, receiver=request.user)
    return render(request, 'chat/chat.html', {'messages': messages, 'receiver_id': receiver_id})


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