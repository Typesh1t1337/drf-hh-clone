import random
from .task import send_confirmation_message
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.middleware import csrf
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

            return Response(token)


class RegisterUserView(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterUserSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = serializer.get_token(user)

            return Response(token)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)

        if serializer.is_valid():
            username = serializer.validated_data['username']
            password = serializer.validated_data['password']

            user = authenticate(
                username=username,
                password=password
            )

            if user is None:
                return Response("Password or Username is incorrect", status=status.HTTP_400_BAD_REQUEST)

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

        if user.is_verified:
            return Response(
                {
                    "message": "Account is already verified",
                }
            )

        user.verification = code
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
        serializer = VerifyEmailSerializer(data=request.data)

        if serializer.is_valid():
            code = serializer.validated_data['email']

            user = request.user

            if user.is_verified:
                return Response(
                    {
                        "message": "Account is already verified",
                    }
                )

            if user.verification == code:
                user.is_verified = True
                user.save()

                return Response(
                    {
                        "message": "Account successfully verified",
                    }
                )
            else:
                return Response(
                    {
                        "message": "Account not verified",
                    }
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)