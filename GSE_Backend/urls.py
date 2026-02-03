
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include('api.urls') ),
    path('api-vendor/v1/', include('api_vendor.urls') ),
    path('api-auth/v1/', include('api_auth.urls') ),
    path('api-ghg/v1/', include('api_ghg.urls') ),
]
