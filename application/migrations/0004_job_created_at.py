# Generated by Django 5.1.5 on 2025-01-27 16:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('application', '0003_job_salary'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
