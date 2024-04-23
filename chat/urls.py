from django.urls import path
from . import views

urlpatterns = [
    path('chat/<int:receiver_id>/', views.chat_view, name='chat'),
    path('send-message/<int:receiver_id>/', views.send_message, name='send_message'),
]