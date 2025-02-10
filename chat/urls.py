from django.urls import path
from .views import *

urlpatterns = [
    path('support/send/', SendMessageToSupportView.as_view(), name='send_message'),
    path('retrieve/', ChatListView.as_view(),name='chat_list'),
    path('retrieve/message/<int:chat_id>/<str:second_user>/', MessageListView.as_view(),name='chat_list'),
]