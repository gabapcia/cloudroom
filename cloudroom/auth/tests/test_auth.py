from django.urls import reverse
from cloudroom.utils.test import BaseTests


class TestAuth(BaseTests):
    def test_login(self, login, client, settings):
        login(need_create=True)

    def test_logout(self, login, client, settings):
        login(need_create=True)
        response = client.post(reverse('logout'))
        cookie_name = settings.JWT_AUTH_REFRESH_COOKIE
        cookie = response.cookies.get(cookie_name, '')
        assert response.status_code == 200
        assert not cookie.value
    
    def test_user_detail(self, client, login):
        login(need_create=True)
        response = client.get(reverse('user-detail'))
        response_data = response.json()
        assert response.status_code == 200
        assert 'username' in response_data
        assert 'first_name' in response_data
        assert 'last_name' in response_data

    def test_refresh_token(self, client, login):
        login(need_create=True)
        response = client.post(reverse('refresh-token'))
        response_data = response.json()
        assert response.status_code == 200
        assert 'access' in response_data
