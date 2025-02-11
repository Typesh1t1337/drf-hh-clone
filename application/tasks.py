from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

from application.models import Job
from chat.models import Chat, Message



@shared_task
def create_chat_and_message_task(job_id:int,first_user:str, second_user:str, last_message:str) -> bool:
    try:
        job = Job.objects.get(id=job_id)
        first_user_obj = get_user_model().objects.get(username=first_user)
        second_user_obj = get_user_model().objects.get(username=second_user)
        chat = Chat.objects.filter(first_user=first_user_obj, second_user=second_user_obj).first()
        if chat:
            chat.last_message = "Assigned"
            chat.save(update_fields=['last_message','last_message_date'])
        else:
            chat = Chat.objects.create(first_user=first_user_obj, second_user=second_user_obj, last_message="Assigned Code:Bober")

        Message.objects.create(chat=chat, message=last_message, sender=first_user, receiver=second_user_obj)

    except ObjectDoesNotExist:
        return False
    return True