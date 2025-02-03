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
]