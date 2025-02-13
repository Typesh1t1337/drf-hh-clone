from django.contrib.auth import get_user_model
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    location = models.ForeignKey("Cities", null=True,on_delete=models.SET_NULL)
    company = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    category = models.ForeignKey('Categories', on_delete=models.CASCADE, null=True)
    salary = models.IntegerField(null=True)
    created_at = models.DateTimeField(auto_now_add=True,null=True)



class Categories(models.Model):
    name = models.CharField(max_length=100)

class Cities(models.Model):
    name = models.CharField(max_length=100)


class Assignments(models.Model):
    status = models.CharField(max_length=100,choices=[('Applied', 'applied'), ('Approved', 'approved'), ('Rejected', 'rejected'),("Archived","archived")])
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE,related_name='user_assignments')
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    company = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, null=True,related_name='companies')

    class Meta:
        unique_together = ('user', 'job')



