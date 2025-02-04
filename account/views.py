import random

from django.contrib.auth import authenticate as auth_authenticate, logout
from django.utils.timezone import now

from .task import send_confirmation_message
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny,IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie

class RegisterCompanyVIew(APIView):
    permission_classes = [AllowAny]


    def post(self,request):
        serializer = RegisterCompanySerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = serializer.get_token(user)

            response = Response({
                "user": user.status
            })

            response.set_cookie(
                key='access',
                value=token['access'],
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/',
            )

            response.set_cookie(
                key='refresh',
                value=token['refresh'],
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/'
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = serializer.get_token(user)

            response = Response({
                "user": user.status
            })

            response.set_cookie(
                key='access',
                value=token['access'],
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/',
            )

            response.set_cookie(
                key='refresh',
                value=token['refresh'],
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/'
            )

            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = auth_authenticate(request, username=username, password=password)

            if user is None:
                return Response(f"Password or Username is incorrect", status=status.HTTP_400_BAD_REQUEST)


            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access = str(refresh.access_token)

            response = JsonResponse({"status": user.status})

            response.set_cookie(
                key='access',
                value=access,
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/',
            )

            response.set_cookie(
                key='refresh',
                value=refresh_token,
                httponly=True,
                max_age=36000,
                samesite="Lax",
                secure=False,
                path='/'
            )


            return response

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({
            'message': 'get csrf token!',
        }, status=status.HTTP_200_OK)


class IsAuthenticatedView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"user":
                             {"status": request.user.status,
                              "username": request.user.username,
                              "isVerified": request.user.is_verified,
                              "email": request.user.email,
                              }})



class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = JsonResponse({
            'status': True,
        })

        response.delete_cookie('access')
        response.delete_cookie('refresh')
        return response


class AccountVerificationCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = random.randint(100000, 999999)

        user = request.user

        if user.last_verification:
            elapsed_time = (now() - user.last_verification).total_seconds()
            remaining_time = 60 - elapsed_time

            if remaining_time > 0:
                return Response({

                        "error": f"{remaining_time} seconds remain",
                          "remain_seconds": int(remaining_time)
                    }, status=status.HTTP_429_TOO_MANY_REQUESTS
                )

        if user.is_verified:
            return Response(
                {
                    "message": "Account is already verified",
                }
            )

        user.verification = code
        user.last_verification = now()
        user.save()

        send_confirmation_message.delay(user.email, code)


        return Response(
            {
                "status": "code successfully sended"
            }
        )


class VerifyEmailView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):

        user = request.user
        serializer = VerifyEmailSerializer(data=request.data)

        if user.is_verified:
            return Response(
                {
                    "message": "Account is already verified",
                },status=status.HTTP_400_BAD_REQUEST
            )


        if serializer.is_valid():
            code = serializer.validated_data['code']

            if user.verification and user.verification == code:
                user.is_verified = True
                user.save()

                return Response(
                    {
                        "message": "Account successfully verified",
                    }, status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {
                        "status": False,
                    }
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        response = JsonResponse({
            'status': True,
        })

        response.delete_cookie('access')

        return response