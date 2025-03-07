import random

from django.conf import settings
from django.contrib.auth import authenticate as auth_authenticate, logout
from django.core.cache import cache
from django.db.models import Count
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser

from application.models import Job, Assignments
from .tasks import send_confirmation_message, create_pdf_cv_task
from django.http import JsonResponse
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import *
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from chat.models import *



class RegisterCompanyVIew(APIView):
    permission_classes = [AllowAny]

    def post(self,request):
        serializer = RegisterCompanySerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            token = serializer.get_token(user)

            #Support always first user, and regular user will be second user only
            chat = Chat.objects.create(first_user_id=4, second_user=user,last_message="Hi, welcome to Job Ondemand, ask question if you encouter with some issues, AI SUPPORT will respond you immediately.")

            Message.objects.create(sender_id=4, receiver=user, message="Hi, welcome to Job Ondemand, ask question if you encouter with some issues, AI SUPPORT will respond you immediately.", chat=chat)



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

            # Support always first user, and regular user will be second user only
            chat = Chat.objects.create(first_user_id=4, second_user=user,
                                       last_message=f"Hi {user.first_name}, welcome to Job Ondemand, ask question if you encouter with some issues, AI SUPPORT will respond you immediately.")

            Message.objects.create(sender_id=4, receiver=user,
                                   message=f"Hi {user.first_name}, welcome to Job Ondemand, ask question if you encouter with some issues, AI SUPPORT will respond you immediately.",
                                   chat=chat)

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
                return Response({
                    'message': 'Invalid username or password',
                }, status=status.HTTP_401_UNAUTHORIZED)


            refresh = RefreshToken.for_user(user)
            refresh_token = str(refresh)
            access = str(refresh.access_token)

            response = JsonResponse({"status": user.status,
                                     "access": access,
                                     "refresh": refresh_token
                                     })

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
        user = request.user
        cache_key = f"user_{user.id}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)



        pfp =f"{settings.MEDIA_URL}{user.photo}" if user.photo else None
        cv = request.build_absolute_uri(user.cv_file) if user.cv_file else None

        data = {
            "user": {
                "status": user.status,
                "username": user.username,
                "isVerified": user.is_verified,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "pfp": pfp,
                "cv": cv,
            }
        }

        cache.set(cache_key, data, timeout=600)

        return Response(data, status=status.HTTP_200_OK)



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


class RetrieveUserView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, username):
        cache_key = f"user_{username}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data, status=status.HTTP_200_OK)

        user = get_user_model().objects.filter(username=username).first()

        if user:
            serializer = ProfileSerializer(user).data

            cache.set(cache_key, serializer, timeout=600)

            return Response(serializer,status=status.HTTP_200_OK)
        else:
            return Response({
                "status": "User does not exist",
            },status=status.HTTP_404_NOT_FOUND
            )


class CompanyVacanciesView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, username):
        try:
            company = get_user_model().objects.get(username=username, status='Company')
        except get_user_model().DoesNotExist:
            return Response({
                "status": "User does not exist",
            },
                status=status.HTTP_404_NOT_FOUND)


        job = Job.objects.filter(company__username=username)


        serializer = CompanyVacanciesSerializer(job, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)




class EditProfileView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser,JSONParser)

    def put(self, request, *args, **kwargs):
        user = request.user
        old_username = user.username

        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            if any(request.data.values()):
                cache.delete(f"user_{old_username}")
                serializer.save()

            return Response({
                "success": "Profile updated successfully"
            }, status=status.HTTP_200_OK)



        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class AddCVView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        user = request.user

        serializer = CvSerializer(data=request.data)

        if serializer.is_valid():
            occupation = serializer.validated_data['occupation']
            skill_sets = serializer.validated_data['skill_sets']
            language = serializer.validated_data['languages']
            address = serializer.validated_data['address']
            work_experience = serializer.validated_data['work_experience']

            cv_obj = CV.objects.create(
                cv_owner=user,
                occupation=occupation,
                skill_sets=skill_sets,
                languages=language,
                address=address,
                work_experience=work_experience,
            )

            create_pdf_cv_task.delay(cv_obj.id)


            return Response(
                {
                    "success": "cv created successfully"
                }, status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class EditCVView(APIView):
    permission_classes = [IsAuthenticated]
    def put(self,request, *args, **kwargs):
        user = request.user

        cv_obj = CV.objects.filter(cv_owner=user).first()

        if not cv_obj:
            return Response({
                "status": "CV not found",
            }, status=status.HTTP_404_NOT_FOUND)

        serializer = CvSerializer(cv_obj, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()

            create_pdf_cv_task.delay(cv_obj.id)

            return Response({
                "success": "CV updated successfully"
            }, status=status.HTTP_200_OK)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class RetrieveCVView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request, username):
        user = get_user_model().objects.filter(username=username).first()

        result = {

        }

        user_info = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "cv_link": user.cv_file.url,
        }

        if not user:
            return Response({
                "status": "User does not exist",
            }, status=status.HTTP_404_NOT_FOUND)

        instant_user = request.user
        if instant_user != user and instant_user.status == "Company":
            cv_obj = CV.objects.filter(cv_owner=user).first()

            if cv_obj:
                result['cv'] = CvSerializer(cv_obj).data
                result["user_info"] = user_info
                return Response(result, status=status.HTTP_200_OK)

            else:
                return Response({
                    "error": "CV not found",
                }, status=status.HTTP_404_NOT_FOUND)

        if instant_user == user:
            cv_obj = CV.objects.filter(cv_owner=user).first()

            if cv_obj:
                assignment = Assignments.objects.filter(user=instant_user).values('status').annotate(count=Count('status'))
                result = {
                    "cv": CvSerializer(cv_obj).data,
                    "user_info": user_info,
                    "assignments": {"applied": 0, "rejected": 0, "accepted": 0}
                }

                status_mapping = {
                    "Applied": "applied",
                    "Rejected": "rejected",
                }


                for entry in assignment:
                    count = entry['count']
                    assign_status = entry['status']

                    key = status_mapping.get(assign_status, "accepted")
                    result["assignments"][key] = count


                return Response(result, status=status.HTTP_200_OK)

        else:
            return Response({
                "error": "You are not allowed to access this page",
            }, status=status.HTTP_403_FORBIDDEN)
