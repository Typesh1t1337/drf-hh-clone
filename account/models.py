from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models

def upload_to(instance, filename):
    return f'user_{instance.username}_{filename}'

def cv_upload_to(instance, filename):
    return f'users_{instance.username}_cv_{filename}'

class User(AbstractUser):
    photo = models.ImageField(upload_to=upload_to,blank=True,null=True,validators=[FileExtensionValidator(['jpg','png', 'webp','jpeg'])])
    phone_number = models.CharField(max_length=11, blank=True,unique=True,null=True)
    status = models.CharField(default=False,max_length=20, blank=True,null=True,choices=(('user','User'),('company', 'Company')))
    is_verified = models.BooleanField(default=False)
    cv = models.FileField(upload_to=cv_upload_to,blank=True,null=True, validators=[FileExtensionValidator(['txt','docx','pdf','png','jpg','jpeg'])])
    verification = models.IntegerField(default=0)
    last_verification = models.DateTimeField(null=True,blank=True)