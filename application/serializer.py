from rest_framework import serializers

from application.models import *


class JobSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.name')
    company = serializers.CharField(source='company.username', read_only=True)
    category = serializers.CharField(source='category.name')
    class Meta:
        model = Job
        fields = '__all__'

    def create(self, validated_data):
        job = Job.objects.create(
            title=validated_data['name'],
            description=validated_data['description'],
            location=validated_data['location'],
            company=validated_data['company'],
            category=validated_data['category'],
            salary=validated_data['salary']
        )

        job.save()

        return job

class ListJobSerializer(serializers.ModelSerializer):
    location = serializers.CharField(source='location.name')
    company = serializers.CharField(source='company.username', read_only=True)

    class Meta:
        model = Job
        fields = ['id', 'title', 'description', 'location', 'category', 'salary', 'company']

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

    class Meta:
        model = Assignments
        fields = ['job_id']


class ApplyJobDetailSerializer(serializers.ModelSerializer):
    job_id = serializers.IntegerField()
    job_title = serializers.CharField(source='job.title')
    job_description = serializers.CharField(source='job.description')
    job_location = serializers.CharField(source='job.location.name')
    job_salary = serializers.CharField(source='job.salary')
    class Meta:
        model = Assignments
        fields = ['status', 'job_title', 'job_description', 'job_location', 'job_salary', 'job_id']