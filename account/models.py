from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.db import models
from django_filters.conf import settings

from .storage import *

def upload_to(instance, filename):
    return f'user_{instance.username}_{filename}'

def cv_upload_to(instance, filename):
    return f'users_{instance.username}_cv_{filename}'

class User(AbstractUser):
    photo = models.ImageField(upload_to=upload_to,blank=True,null=True,validators=[FileExtensionValidator(['jpg','png', 'webp','jpeg'])], storage=CustomStorage())
    phone_number = models.CharField(max_length=11, blank=True,unique=True,null=True)
    status = models.CharField(default=False, max_length=20, blank=True,null=True,choices=(('user','User'),('company', 'Company')))
    is_verified = models.BooleanField(default=False)
    cv_file = models.FileField(upload_to=cv_upload_to, blank=True,null=True, validators=[FileExtensionValidator(['txt', 'docx', 'pdf', 'png', 'jpg', 'jpeg'])], storage=CustomStorage())
    verification = models.IntegerField(default=0)
    last_verification = models.DateTimeField(null=True,blank=True)
    cv_profile = models.OneToOneField('CV', null=True,on_delete=models.SET_NULL)



class CV(models.Model):
    cv_owner = models.OneToOneField(get_user_model(), on_delete=models.CASCADE, related_name='user_cv')
    occupation = models.ForeignKey('application.Categories', on_delete=models.CASCADE)
    skill_sets = models.CharField(null=False)
    languages = models.CharField(null=False)
    address = models.CharField(null=False)
    work_experience = models.CharField(blank=True,null=False)


