from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    photo = models.ImageField(upload_to='photos/%Y/%m/%d/',blank=True,null=True)
    phone_number = models.CharField(max_length=11, blank=True,unique=True,null=True)
    status = models.CharField(default=False,max_length=20, blank=True,null=True,choices=(('user','User'),('company', 'Company')))
    is_verified = models.BooleanField(default=False)
    cv = models.FileField(upload_to='cvs/%Y/%m/%d/',blank=True,null=True)
