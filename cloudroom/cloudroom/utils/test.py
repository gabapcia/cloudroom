from django.urls import reverse
from random import choice
from string import ascii_letters
from abc import ABC
import pytest


class BaseTests(ABC):
    @pytest.fixture
    def create_user(self, django_user_model):
        def create(username=None, password=None, admin=False):
            gen = lambda: ''.join(choice(ascii_letters) for _ in range(15))
            user_data = {
                'username': username or gen(),
                'password': password or gen(),
            }
            user = (
                django_user_model.objects.create_user(**user_data)
                if not admin
                else django_user_model.objects.create_admin_user(**user_data)
            )

            return user_data
        
        return create

    @pytest.fixture
    def login(self, client, create_user, settings):
        def do_login(need_create=False, user={}, **user_kw):
            if need_create:
                user = create_user(**user_kw)
            elif not user:
                raise ValueError('User not provied')

            response = client.post(reverse('login'), user)
            response_data = response.json()
            assert response.cookies.get(settings.JWT_AUTH_REFRESH_COOKIE, None)
            assert response.status_code == 200
            assert 'access' in response_data
            assert 'refresh' in response_data
            assert 'user' in response_data

            return response
        
        return do_login
