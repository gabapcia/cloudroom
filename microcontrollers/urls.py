from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views


router = DefaultRouter()
router.register(r'boards', views.BoardViewSet)
router.register(r'pins', views.PinViewSet)
router.register(r'periodic-pins', views.PeriodicPins)


urlpatterns = [
    path('', include(router.urls)),
]
