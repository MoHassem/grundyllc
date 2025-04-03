
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include

urlpatterns = [
    path('', include('storefront.urls')),
    path('admin/', admin.site.urls),
    path('config/', include('config.urls')),
]
