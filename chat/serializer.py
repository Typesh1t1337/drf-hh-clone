from rest_framework import serializers

from chat.models import *


class ChatWithSupportSerializer(serializers.ModelSerializer):
    message = serializers.CharField(write_only=True)
    class Meta:
        model = Message
        fields = ['message']

class ChatSerializer(serializers.ModelSerializer):
    first_username = serializers.CharField(read_only=True, source='first_user.username')
    second_username = serializers.CharField(read_only=True, source='second_user.username')
    class Meta:
        model = Chat
        fields = ['pk', 'first_username', 'second_username', 'last_message']


class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(read_only=True,source='sender.username')
    receiver = serializers.CharField(read_only=True,source='receiver.username')
    class Meta:
        model = Message
        fields = ['pk', 'message', 'sender', 'receiver', 'message_date', 'is_read','job_link']
