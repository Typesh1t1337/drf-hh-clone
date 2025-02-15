from django.urls import path

from .views import *

urlpatterns = [
    path('job/list/', ListJobsView.as_view(), name='job_list'),
    path('job/create/', CreateJobView.as_view(), name='job_create'),
    path('job/cities/', ListAllCitiesView.as_view(), name='job_cities'),
    path('job/categories/', ListAllCategoriesView.as_view(), name='job_categories'),
    path('job/apply/', ApplyJobView.as_view(), name='job_apply'),
    path('job/info/<int:job_id>/',JobInfoView.as_view()),
    path('job/similar/<int:job_id>/',SimilarJobView.as_view()),
    path('job/applies/',RetrieveAllAppliesView.as_view(), name='job_applies'),
    path('job/create/,',CreateJobView.as_view(), name='job_create'),
    path('job/check/status/<int:job_id>/', JobApplyStatusView.as_view()),
    path('job/company/vacancies/', RetrieveCompanyVacanciesView.as_view()),
    path('job/remove/<int:job_id>/',DeleteVacancyView.as_view()),
    path('job/assignments/retrieve/', RetrieveAllCompanyAppliesView.as_view()),
    path('job/approve/', ApproveApplyView.as_view()),
    path('job/reject/', RejectApplyView.as_view()),
    path('job/archive/', ArchiveApplyView.as_view()),
    path('job/delete/', DeleteFromAchieveView.as_view()),
    path('job/list/landing/', ListFirst20Jobs.as_view())
]