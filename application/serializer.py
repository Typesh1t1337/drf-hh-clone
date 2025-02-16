from rest_framework import serializers

from application.models import *


class JobCreateSerializer(serializers.ModelSerializer):
    location = serializers.SlugRelatedField(slug_field='name',queryset=Cities.objects.all(),required=True)
    category = serializers.SlugRelatedField(slug_field='name',queryset=Categories.objects.all(),required=True)
    class Meta:
        model = Job
        fields = ['title', 'description', 'location', 'salary', 'category']



class JobSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.name')
    company = serializers.CharField(source='company.username', read_only=True)
    category = serializers.CharField(source='category.name')
    class Meta:
        model = Job
        fields = '__all__'



class ListJobSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.name')
    company = serializers.CharField(source='company.username', read_only=True)
    status = serializers.CharField(read_only=True)
    chat_id = serializers.CharField(read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'category', 'salary', 'company', 'status', 'chat_id']

class ListAllCitiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cities
        fields = '__all__'


class ListAllCategoriesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Categories
        fields = '__all__'


class ApplyJobSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField()
    company = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all(),required=True)

    class Meta:
        model = Assignments
        fields = ['job_id', 'company']


class ApplyJobDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField()
    job_title = serializers.CharField(source='job.title')
    job_description = serializers.CharField(source='job.description')
    job_location = serializers.CharField(source='job.location.name')
    job_salary = serializers.CharField(source='job.salary')
    class Meta:
        model = Assignments
        fields = ['status', 'job_title', 'job_description', 'job_location', 'job_salary', 'job_id']


class AppliedUserDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField()
    job_title = serializers.CharField(source='job.title')
    user_username = serializers.CharField(source='user.username')
    user_email = serializers.CharField(source='user.email')

    class Meta:
        model = Assignments
        fields = ['status', 'job_id', 'job_title', 'user_username', 'user_email']


class ApplyUserResultSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField()
    user = serializers.SlugRelatedField(slug_field='username', queryset=get_user_model().objects.all(), required=True)
    class Meta:
        model = Assignments
        fields = ['job_id', 'user']
