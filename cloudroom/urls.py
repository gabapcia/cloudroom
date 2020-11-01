from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('api/admin/', admin.site.urls),
    path('api/microcontrollers/', include('microcontrollers.urls')),
    path('api/auth/', include('auth.urls')),
]
