import django_filters
from django.db.models import Q

from .models import *
class JobFilter(django_filters.FilterSet):
    search = django_filters.CharFilter(method='search_jobs')
    salary_min = django_filters.CharFilter(field_name='salary', lookup_expr='gte', label="Search Salary Min")
    salary_max = django_filters.CharFilter(field_name='salary', lookup_expr='lte', label="Search Salary Max")
    location = django_filters.CharFilter(field_name='location__name', lookup_expr='icontains',label="Search Location by Name")
    category = django_filters.CharFilter(field_name='category__name', lookup_expr='icontains', label="Search Categories")

    class Meta:
        model = Job
        fields = ['search', 'salary_min', 'salary_max', 'location', 'category']

    def search_jobs(self, queryset, name, value):
        if value:
            return queryset.filter(Q(title__icontains=value) | Q(description__icontains=value))
        return queryset



class ApplyFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status', lookup_expr='icontains', label="Search Status")



class SkillsFilter(django_filters.FilterSet):
    related_names = django_filters.CharFilter(field_name='related_skills__name', lookup_expr='icontains', label="Search Related Names")
