from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from jobondemand.settings import EMAIL_HOST_USER

@shared_task
def send_confirmation_message(email: str, code: int) -> bool:

    try:
        subject = 'Confirm your email'
        from_email = EMAIL_HOST_USER
        recipient_list = [email]

        user = get_user_model().objects.get(email=email)

        credentials = {
            'user': user.username,
            'code': code,
        }

        html_content = render_to_string("email/email.html", credentials)

        email_message = EmailMessage(subject, html_content, from_email, recipient_list)
        email_message.content_subtype = 'html'
        email_message.send()
    except Exception as e:
        print(e)

    return True
