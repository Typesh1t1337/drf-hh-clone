import django_filters
from .models import *
class JobFilter(django_filters.FilterSet):
    title = django_filters.CharFilter(field_name='title', lookup_expr='icontains', label="Search Job Title")
    description = django_filters.CharFilter(field_name='description', lookup_expr='icontains', label="Search Job Description")
    salary_min = django_filters.CharFilter(field_name='salary', lookup_expr='icontains', label="Search Salary Min")
    salary_max = django_filters.CharFilter(field_name='salary', lookup_expr='icontains', label="Search Salary Max")
    location = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains',label="Search Location by Name")
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains', label="Search Categories")


class ApplyFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains', label="Search Status")