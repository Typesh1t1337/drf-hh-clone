from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from application.filters import JobFilter
from application.models import Job,Cities,Categories
from application.serializer import JobSerializer, ListAllCitiesSerializer, ListJobSerializer, \
    ListAllCategoriesSerializer


class CreateJobView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request):
        user = request.user

        if user.status != "Company":
            return Response({
                "error": "User is not a company"
            })

        serializer = JobSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=user)

            return Response(serializer.data)

        return Response(serializer.errors, status=400)



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


