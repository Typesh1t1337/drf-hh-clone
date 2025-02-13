from django.contrib.auth import get_user_model
from rest_framework import filters, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from application.filters import JobFilter, ApplyFilter
from application.serializer import *
from application.tasks import create_chat_and_message_task,approve_task,reject_task

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

        if not user.is_verified:
            return Response(
                {
                    "error": "Users email  is not verified"
                },status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplyJobSerializer(data=request.data)

        if serializer.is_valid():
            job_id = serializer.validated_data['job_id']
            company = serializer.validated_data['company']


            try:
                job = Job.objects.get(pk=job_id)

                is_assign = Assignments.objects.filter(job_id=job_id, user=user, status="Applied", company=company).exists()

                if is_assign:
                    return Response(
                        {
                            "error": "Job already applied"
                        }, status=status.HTTP_400_BAD_REQUEST
                    )

                assign = Assignments.objects.create(job=job, user=user, status="Applied", company=company)
                create_chat_and_message_task.delay(job_id=job_id, first_user=user.id, second_user=company.id, last_message=f"I have assigned to {company.username}, to vacancy {job.title}")
                assign.save()

                if not create_chat_and_message_task.result():
                    return Response(
                        {
                            "error": "Job assigned failed"
                        }, status=status.HTTP_404_NOT_FOUND
                    )

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



class JobApplyStatusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,job_id):
        if Job.objects.filter(job_id=job_id).exists():

            assign = Assignments.objects.filter(job_id=job_id, user=request.user).exists()

            if assign:
                assign_status = Assignments.objects.get(job_id=job_id, user=request.user).status

                return Response({
                    "status": assign_status,
                },
                    status=status.HTTP_200_OK)

            else:
                return Response({
                    "status": "Not applied",
                },
                    status=status.HTTP_200_OK
                )

        else:
            return Response({
                "error": "Job does not exist",
            },
                status=status.HTTP_404_NOT_FOUND
            )

class PaginateApplies(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class RetrieveAllCompanyAppliesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    filterset_class = ApplyFilter
    queryset = Assignments.objects.all()
    serializer_class = AppliedUserDetailSerializer
    pagination_class = PaginateApplies

    def get_queryset(self, *args, **kwargs):
        user = self.request.user
        return Assignments.objects.filter(company=user)


class RetrieveCompanyVacanciesView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    queryset = Job.objects.all()
    serializer_class = ListJobSerializer

    def get_queryset(self):
        user = self.request.user
        return Job.objects.filter(company=user)




class DeleteVacancyView(APIView):
    permission_classes = [IsAuthenticated]
    def delete(self, request,job_id):
        user = request.user

        if Job.objects.filter(pk=job_id,company=user).exists():
            job = Job.objects.get(pk=job_id)
            job.delete()

            return Response(
                {
                    "message": "Job deleted",
                },status=status.HTTP_200_OK
            )
        else:
            return Response({
                "error": "Job does not exist or you dont have access",
            })


class ApproveApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        company = request.user

        if company.status == "User":
            return Response(
                {
                    "error": "User have no permission to approve job",
                },status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplyUserResultSerializer(data=request.data)

        if serializer.is_valid():
            job_id = serializer.validated_data['job_id']
            user = serializer.validated_data['user']

            job = Job.objects.get(pk=job_id)

            if Assignments.objects.filter(job_id=job_id, user=user,status="Approved").exists():
                return Response({
                    "error": "Job already approved",
                },status=status.HTTP_406_NOT_ACCEPTABLE)
            else:
                assignment = Assignments.objects.get(job_id=job_id, user=user)
                assignment.status = "Approved"
                assignment.save()

                approve_task.delay(company_id=company.pk, user_id=user.pk, message=f"Hi,{user.first_name}, your assignment to {job.title} is now approved! Lets discuss about appointment to interview! All regards, {company.first_name} {company.last_name}, {company.username}!")


                return Response({
                    "message": "Job approved",
                }, status=status.HTTP_200_OK)


        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RejectApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        company = request.user

        if company.status == "User":
            return Response(
                {
                    "error": "User have no permission to reject job",
                }, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplyUserResultSerializer(data=request.data)

        if serializer.is_valid():
            job_id = serializer.validated_data['job_id']
            user = serializer.validated_data['user']

            job = Job.objects.get(pk=job_id)

            if Assignments.objects.filter(job=job, user=user,status="Rejetcted").exists():
                return Response({
                    "error": "Job already rejected",
                }, status=status.HTTP_400_BAD_REQUEST)

            else:
                assignment = Assignments.objects.get(job=job, user=user)

                assignment.status = "Rejected"
                assignment.save()
                reject_task.delay(company_id=company.id,user_id=user.id,message=f"Hi,{user.first_name}, Unfortunately, your assignment to vacancy {job.title}, has been rejected,We will be glad to see your assignments to out other vacancies, All regards, {company.first_name} {company.last_name}, {company.username}!")

                return Response({
                    "message": "Job rejected",
                },status=status.HTTP_200_OK)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )

class ArchiveApplyView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        company = request.user

        if company.status == "User":
            return Response(
                {
                    "error": "User have no permission to reject job",
                }, status=status.HTTP_403_FORBIDDEN
            )

        serializer = ApplyUserResultSerializer(data=request.data)

        if serializer.is_valid():
            job_id = serializer.validated_data['job_id']
            user = serializer.validated_data['user']

            job = Job.objects.get(pk=job_id)

            if Assignments.objects.filter(job=job, user=user, status="Archived").exists():
                return Response({
                    "error": "Job already Archived",
                }, status=status.HTTP_400_BAD_REQUEST)

            else:
                assignment = Assignments.objects.get(job=job, user=user)

                assignment.status = "Archived"
                assignment.save()


                return Response({
                    "message": "Job Archived",
                }, status=status.HTTP_200_OK)

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )
