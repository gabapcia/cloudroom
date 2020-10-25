from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/room/', include('boards.urls')),
    path('api/tracking/', include('orders.urls')),
    path('api/christine/', include('christine.urls')),
    path('api/auth/', include('auth.urls')),
]
