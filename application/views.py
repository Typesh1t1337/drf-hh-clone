from django.contrib.auth import get_user_model
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from application.filters import JobFilter, ApplyFilter
from application.models import *
from application.serializer import *


class CreateJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user

        if user.status != "Company":
            return Response({
                "error": "User is not a company"
            }, status=status.HTTP_400_BAD_REQUEST)

        serializer = JobCreateSerializer(data=request.data)

        if serializer.is_valid():
            job = Job.objects.create(
                company=user,
                salary=serializer.validated_data['salary'],
                description=serializer.validated_data['description'],
                location=serializer.validated_data['location'],
                category=serializer.validated_data['category'],
                title=serializer.validated_data['title'],
            )

            return Response(serializer.data, status=status.HTTP_201_CREATED)


        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)



class PaginationJob(PageNumberPagination):
    page_size = 30
    page_size_query_param = 'page_size'

class ListJobsView(generics.ListAPIView):
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend,filters.OrderingFilter,filters.SearchFilter]
    serializer_class = ListJobSerializer
    ordering = ['-created_at']
    ordering_fields = ['created_at', 'salary']
    pagination_class = PaginationJob
    queryset = Job.objects.all()
    filterset_class = JobFilter


class ListAllCitiesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ListAllCitiesSerializer
    queryset = Cities.objects.all()



class ListAllCategoriesView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = ListAllCategoriesSerializer
    queryset = Categories.objects.all()


class ApplyJobView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        user = request.user

        if user.status == "Company":
            return Response(
                {
                    "error": "User is not a company"
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ApplyJobSerializer(data=request.data)

        if serializer.is_valid():
            job_id = serializer.validated_data['job_id']

            try:
                job = Job.objects.get(pk=job_id)

                is_assign = Assignments.objects.filter(job_id=job_id, user=user,status="Applied").exists()

                if is_assign:
                    return Response(
                        {
                            "error": "Job already applied"
                        }, status=status.HTTP_400_BAD_REQUEST
                    )

                assign = Assignments.objects.create(job=job, user=user, status="Applied")

                assign.save()

                return Response(
                    {
                        "message": "Job applied",
                    },
                    status=status.HTTP_200_OK
                )

            except Job.DoesNotExist:
                return Response(
                    {
                        "error": "Job does not exist",
                    },status=status.HTTP_400_BAD_REQUEST
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class JobInfoView(APIView):
    permission_classes = [AllowAny]

    def get(self,request, job_id):
        response = {

        }

        try:
            job = Job.objects.get(pk=job_id)
            response['job_info'] = JobSerializer(job).data

            if request.user.is_authenticated:
                user = request.user

                is_applied = Assignments.objects.filter(job_id=job_id, user=user).exists()

                if is_applied:
                    assignment = Assignments.objects.get(job_id=job_id, user=user)

                    response['status'] = assignment.status
                else:
                    response['status'] = "Not applied"


            return Response(response, status=status.HTTP_200_OK)

        except Job.DoesNotExist:
             return Response({
                    "error": "Job does not exist",
                }, status=status.HTTP_404_NOT_FOUND
             )


class SimilarJobView(APIView):
    permission_classes = [AllowAny]

    def get(self,request,job_id):
        try:
            job_category = Job.objects.get(pk=job_id).category

            similar_jobs = Job.objects.filter(category=job_category).exclude(pk=job_id)[:3].values()

            return Response(
                similar_jobs,status=status.HTTP_200_OK
            )
        except Job.DoesNotExist:
            return Response({
                "error": "Job does not exist",
            },
            status=status.HTTP_404_NOT_FOUND)


class RetrieveAllAppliesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filterset_class = ApplyFilter
    serializer_class = ApplyJobDetailSerializer
    queryset = Assignments.objects.all()

    def get_queryset(self):
        return Assignments.objects.filter(user=self.request.user)


