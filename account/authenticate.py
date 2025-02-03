from django.conf import settings
from rest_framework_simplejwt import authentication as jwt_authentication
from rest_framework import exceptions,authentication

# def enforce_csrf(request):
#     check = authentication.CSRFCheck(request)
#     reason = check.process_view(request, None, None, None)
#     if reason:
#         raise exceptions.AuthenticationFailed(reason)


class CustomTokenAuthentication(jwt_authentication.JWTAuthentication):
    def authenticate(self, request):
       raw_token = request.COOKIES.get('access')

       if not raw_token:
           return None

       validated_token = self.get_validated_token(raw_token)

       user = self.get_user(validated_token)

       return user, validated_token

