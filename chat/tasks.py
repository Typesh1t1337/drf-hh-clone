from celery import shared_task
from django.contrib.auth import get_user_model
from dotenv import load_dotenv
from openai import OpenAI
import os
from .models import Message, Chat

@shared_task
def celery_message_to_support(text:str, first_name:str) -> str:
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")

    help_prompt = f"You are virtual assistant of website called Job on demand its a website as a indeed, there simple system, people apply for hiring, and waiting for invitation, you will help for users, to achieve their goals and targets. The users name that you helping right know is {first_name}."

    openai = OpenAI(api_key=openai_api_key)

    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            store=True,
            messages=[{
                "role": "system",
                "content": help_prompt
            },
                {
                    "role": "user",
                    "content": text
                }
            ]
        )

        reply = response.choices[0].message.content

        return reply


    except Exception as e:
        return str(e)



@shared_task
def celery_chat(text: str, sender: str, receiver: str, chat_id: int) -> bool:
    message = Message.objects.create(sender_username=sender, receiver_username=receiver, message=text, chat_id=chat_id)
    message.save()

    return True

