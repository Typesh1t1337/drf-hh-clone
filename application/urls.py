from django.urls import path

from .views import *

urlpatterns = [
    path('job/list/', ListJobsView.as_view(), name='job_list'),
    path('job/create/', CreateJobView.as_view(), name='job_create'),
    path('job/cities/', ListAllCitiesView.as_view(), name='job_cities'),
    path('job/categories/', ListAllCategoriesView.as_view(), name='job_categories'),
]