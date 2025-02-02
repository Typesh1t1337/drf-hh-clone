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
            access = str(refresh.access_token)

            response = JsonResponse({"status": user.status})

            response.set_cookie(
                key='Authorization',
                value=access,
                httponly=True,
                max_age=36000,
                samesite="None",
                secure=False,
                path='/',
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
        return Response({
            'status': True,
            'user': request.user,
        })