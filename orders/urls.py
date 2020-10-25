from django.urls import path, include
from rest_framework.routers import DefaultRouter
from orders import views


router = DefaultRouter()
router.register(r'correios', viewset=views.CorreiosViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
