import os

from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q

from application.models import Job
from chat.models import Chat, Message
import requests
from dotenv import load_dotenv


@shared_task
def create_chat_and_message_task(job_id: int, first_user: int, second_user: int, last_message: str):
    first_user_obj = get_user_model().objects.get(pk=first_user)
    second_user_obj = get_user_model().objects.get(pk=second_user)
    job = Job.objects.get(pk=job_id)
    try:
        chat = Chat.objects.filter(Q(first_user=first_user_obj, second_user=second_user_obj) | Q(first_user=second_user_obj, second_user=first_user_obj)).first()
        if chat:
            chat.last_message = "Assigned code:Bober"
            chat.save(update_fields=['last_message', 'last_message_date'])
            Message.objects.create(chat=chat, message=last_message, sender=first_user_obj, receiver=second_user_obj, job_link=job)
        else:
            chat = Chat.objects.create(first_user=first_user_obj, second_user=second_user_obj, last_message="Assigned Code:Bober")
            Message.objects.create(chat=chat, message=last_message, sender=first_user_obj, receiver=second_user_obj, job_link= job)


    except ObjectDoesNotExist:
        return False
    return True

@shared_task
def approve_task(company_id:int, user_id:int,message:str):
    company = get_user_model().objects.get(pk=company_id)
    user = get_user_model().objects.get(pk=user_id)

    try:
        chat = Chat.objects.filter(Q(first_user=company, second_user_id=user) | Q(first_user=user, second_user=company)).first()
        if chat:
            chat.last_message = "Approved Code:Lisi4ka"
            chat.save(update_fields=['last_message', 'last_message_date'])
            Message.objects.create(chat=chat, message=message, sender=company, receiver=user)
        else:
            chat = Chat.objects.create(first_user=user, second_user=company, last_message="Approved Code:Lisi4ka")
            Message.objects.create(chat=chat, message=message, sender=company, receiver=user)
    except ObjectDoesNotExist:
        return False

    return True

@shared_task
def reject_task(company_id: int, user_id: int, message: str):
    company = get_user_model().objects.get(pk=company_id)
    user = get_user_model().objects.get(pk=user_id)

    try:
        chat = Chat.objects.filter(Q(first_user=company, second_user_id=user) | Q(first_user=user, second_user=company)).first()

        if chat:
            chat.last_message = "Rejected Code:Lisi4ka"
            chat.save(update_fields=['last_message', 'last_message_date'])
            Message.objects.create(chat=chat, message=message, sender=company, receiver=user)
        else:
            chat = Chat.objects.create(first_user=user, second_user=company, last_message=message)
            Message.objects.create(chat=chat, message=message, sender=company, receiver=user)
    except ObjectDoesNotExist:
        return False

    return True


@shared_task
def request_google_task(city: str):
    load_dotenv()
    API_KEY = os.getenv("GOOGLE_API_KEY")

    response = requests.get(f"https://maps.googleapis.com/maps/api/place/autocomplete/json?input={city}&key={API_KEY}")
    if(response.status_code == 200):
        data = response.json()
        return data["predictions"]
    return {
        "error": "Invalid City"
    }

