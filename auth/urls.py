from django.urls import path
from .views import (
    TokenCookieRefreshView,
    LoginView,
    LogoutView,
    UserDetailsView,
)


urlpatterns = [
    path('refresh/', TokenCookieRefreshView.as_view(), name='refresh-token'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserDetailsView.as_view(), name='user-detail'),
]
