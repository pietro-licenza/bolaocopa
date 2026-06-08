from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('users.urls')),
    path('', include('pools.urls')),
    path('', include('predictions.urls')),
    path('', include('matches.urls')),
]