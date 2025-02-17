from rest_framework_simplejwt.views import TokenRefreshView
from django.urls import path
from .views import *

urlpatterns = [
    path('login/', LoginView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/company/', RegisterCompanyVIew.as_view(), name='register'),
    path('register/user/', RegisterUserView.as_view()),
    path('auth/check/', IsAuthenticatedView.as_view(), name='is_authenticated'),
    path('verify/send_code/',AccountVerificationCodeView.as_view()),
    path('verify/email/', VerifyEmailView.as_view()),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/info/<str:username>/',RetrieveUserView.as_view(), name='user_info'),
    path('company/vacancies/<str:username>/', CompanyVacanciesView.as_view()),
    path('profile/edit/',EditProfileView.as_view(), name='update_profile'),
    path('profile/upload/cv/', AddCVView.as_view(), name='upload_cv'),
]