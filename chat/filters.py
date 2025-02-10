import django_filters
from django.contrib.auth import get_user_model
from django.db.models import Q

from chat.models import Chat


class ChatFilter(django_filters.FilterSet):
    username = django_filters.CharFilter(method='filter_by_username')

    class Meta:
        model = Chat
        fields = ['username']

    def filter_by_username(self, queryset, name, value):
        if value:
            try:
                return queryset.filter(
                                        Q(first_user__username__icontains=value, second_user=self.request.user)
                                        |
                                        Q(first_user=self.request.user, second_user__username__icontains=value)
                )
            except get_user_model().DoesNotExist:
                return queryset.none()

        return queryset