from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

schemas_view = get_schema_view(
    openapi.Info(
        title="Jobondemand account API",
        default_version='v1',
        description="Jobondemand account API",
        terms_of_service="https://www.jobondemand.com/terms/",
        contact=openapi.Contact(email="arnurzhhaill@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny]
)

