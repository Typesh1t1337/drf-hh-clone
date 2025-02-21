import time

from django.db.models import Q
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from chat.models import Chat
from .filters import ChatFilter
from .serializer import *
from chat.tasks import *
from .middleware import *
from .middleware import *
class SendMessageToSupportView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user

        chat = Chat.objects.get(first_user_id=4, second_user=user)

        serializer = ChatWithSupportSerializer(data=request.data)


        if serializer.is_valid():
            message = serializer.validated_data['message']

            chat.last_message = message
            chat.save(update_fields=['last_message'])


            message_obj = Message.objects.create(sender=user, receiver_id=4, message=message, chat=chat, is_read=True)


            celery_result = celery_message_to_support.delay(text=message, first_name =user.first_name)


            while not celery_result.ready():
                time.sleep(1)

            result = celery_result.result

            chat.last_message = result
            chat.save(update_fields=['last_message', 'last_message_date'])

            message = Message.objects.create(sender_id=4, receiver=user, message=result, chat=chat)

            return Response(
                {
                    "message": result
                },status=status.HTTP_200_OK
            )



        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class ChatListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Chat.objects.all()
    serializer_class = ChatSerializer
    filterset_class = ChatFilter
    filter_backends = (DjangoFilterBackend,)
    ordering_fieilds = ('-last_message_date')
    def get_queryset(self):
        user = self.request.user
        return super().get_queryset().filter(Q(first_user=user) | Q(second_user=user)).order_by('-last_message_date')


class MessageListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request,chat_id,second_user):
        user = request.user

        result = {

        }
        if Chat.objects.filter(Q(id=chat_id, second_user=user, first_user__username=second_user) | Q(id=chat_id, first_user=user,second_user__username=second_user)).exists():
            not_read_messages = Message.objects.filter(chat_id=chat_id,is_read=False)
            not_read_messages.filter(receiver=user).update(is_read=True)
            all_messages = Message.objects.filter(chat_id=chat_id).order_by('message_date')

            serializer = MessageSerializer(all_messages, many=True)

            result['messages'] = serializer.data

            second_user_obj = get_user_model().objects.get(username=second_user)

            if second_user_obj:
                result['is_online'] = check_user_online(second_user_obj.pk)

            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response({
                "error": "Chat with this id does not exist"
            },
                status=status.HTTP_404_NOT_FOUND)


