from django.contrib.auth import get_user_model
from django.core.validators import ValidationError
from django.db import models


class Chat(models.Model):
    first_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='chat_first_user')
    second_user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='chat_second_user')
    last_message = models.TextField()
    last_message_date = models.DateTimeField(auto_now=True)



    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['first_user', 'second_user'], name='unique_chat'
            ),
        ]

def file_validation(file):
    if file.size > 10240:
        raise ValidationError(
            'File too big. File size should be less than 10240.'
        )


class Message(models.Model):
    sender = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='message_user')
    receiver = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='message_company')
    message = models.TextField()
    message_date = models.DateTimeField(auto_now=True)
    is_read = models.BooleanField(default=False)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    file = models.FileField(upload_to='messages', validators=[file_validation],null=True,blank=True)
    job_link = models.ForeignKey('application.Job', on_delete=models.CASCADE, null=True, blank=True)


