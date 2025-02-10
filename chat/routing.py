from django.urls import path

from chat import consumers

websocket_urlpatterns = [
    # path("ws/chat/<int:chat_id>/", consumers.ChatConsumer.as_asgi()),
    path("ws/chat/support/<int:chat_id>/", consumers.ChatConsumer.as_asgi()),
]