
from django.urls import path, include

urlpatterns = [
    path('', include('storefront.urls')),
    path('config/', include('config.urls')),

]
