import pytest
from django.conf import settings
from django.urls import reverse
from .base import BaseAuthTests


class TestJWT(BaseAuthTests):
    refresh_token_url = reverse('refresh-token')
    login_url = reverse('login')
    logout_url = reverse('logout')
    user_detail_url = reverse('user-detail')

    def login(self, client, user_data, use_email=False):
        data = {'password': user_data['password']}
        if use_email:
            data['email'] = user_data['email']
        else:
            data['username'] = user_data['username']

        return client.post(
            TestJWT.login_url,
            data,
            content_type='application/json',
        )

    def logout(self, client):
        return client.post(TestJWT.logout_url, content_type='application/json')

    @pytest.mark.parametrize('use_email', [True, False])
    def test_login(self, user, client, use_email):
        resp = self.login(client=client, user_data=user[1], use_email=use_email)
        assert resp.status_code == 200

        assert settings.JWT_AUTH_REFRESH_COOKIE in resp.cookies
        assert bool(resp.cookies[settings.JWT_AUTH_REFRESH_COOKIE].value)

        resp_data = resp.json()
        assert 'access' in resp_data
        assert 'refresh' in resp_data
        assert 'user' in resp_data

    def test_login_without_credentials(self, user, client):
        login_url = TestJWT.login_url
        resp = client.post(login_url, {}, content_type='application/json')
        assert resp.status_code == 400

    def test_logout(self, user, client):
        self.login(client=client, user_data=user[1])
        resp = self.logout(client=client)
        assert resp.status_code == 200
        assert not bool(resp.cookies[settings.JWT_AUTH_REFRESH_COOKIE].value)

    def test_user_detail_authenticated(self, client, user):
        user_data = user[1]
        self.login(client=client, user_data=user[1])
        
        resp = client.get(TestJWT.user_detail_url)
        assert resp.status_code == 200
        
        resp_data = resp.json()
        assert user_data['username'] == resp_data['username']
        assert user_data['first_name'] == resp_data['first_name']
        assert user_data['last_name'] == resp_data['last_name']
        assert user_data['email'] == resp_data['email']

    def test_user_detail_unauthenticated(self, client):
        resp = client.get(TestJWT.user_detail_url)
        assert resp.status_code == 403

    def test_refresh_token_with_header(self, client, user):
        self.login(client=client, user_data=user[1])

        resp = client.post(
            TestJWT.refresh_token_url,
            content_type='application/json',
        )
        assert resp.status_code == 200
        resp_data = resp.json()
        assert 'access' in resp_data
        assert bool(resp_data['access'])
    
    def test_refresh_token_with_body(self, client, user):
        token = self.login(client=client, user_data=user[1]).json()['refresh']

        resp = client.post(
            TestJWT.refresh_token_url,
            {'refresh': token},
            content_type='application/json',
        )
        assert resp.status_code == 200
        resp_data = resp.json()
        assert 'access' in resp_data
        assert bool(resp_data['access'])

    def test_refresh_token_invalid(self, client, user):
        self.login(client=client, user_data=user[1])

        resp = client.post(
            TestJWT.refresh_token_url,
            {'refresh': 'invalid token'},
            content_type='application/json',
        )
        assert resp.status_code == 401
