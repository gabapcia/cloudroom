from django.urls import path
from .views import (
    TokenCookieRefreshView,
    LoginView,
    LogoutView, 
    UserDetailsView
)
from django.conf import settings


urlpatterns = [
    path('refresh/', TokenCookieRefreshView.as_view(), name='token'),
    path('login/', LoginView.as_view(), name='login'),
    # logged in only
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetailsView.as_view(), name='user_details'),
]
