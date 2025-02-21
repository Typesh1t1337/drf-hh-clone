from rest_framework import serializers

from chat.models import *
from .middleware import check_user_online


class ChatWithSupportSerializer(serializers.ModelSerializer):
    message = serializers.CharField(write_only=True)
    class Meta:
        model = Message
        fields = ['message']

class ChatSerializer(serializers.ModelSerializer):
    first_username = serializers.CharField(read_only=True, source='first_user.username')
    second_username = serializers.CharField(read_only=True, source='second_user.username')
    first_user_online = serializers.SerializerMethodField()
    second_user_online = serializers.SerializerMethodField()
    class Meta:
        model = Chat
        fields = ['pk', 'first_username', 'second_username', 'last_message','first_user_online', 'second_user_online']


    def get_first_user_online(self, obj):
        user_id = obj.first_user.id
        return check_user_online(user_id)

    def get_second_user_online(self, obj):
        user_id = obj.second_user.id
        return check_user_online(user_id)

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.CharField(read_only=True, source='sender.username')
    receiver = serializers.CharField(read_only=True, source='receiver.username')
    class Meta:
        model = Message
        fields = ['pk', 'message', 'sender', 'receiver', 'message_date', 'is_read','job_link']
