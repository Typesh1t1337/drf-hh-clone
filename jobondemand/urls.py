from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("account.urls")),
    path("api/v1/", include("application.urls")),
    path("api/chat/", include("chat.urls")),
]
