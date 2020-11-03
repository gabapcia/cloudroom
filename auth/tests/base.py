import string
import random
from contextlib import suppress
from abc import ABC
import pytest
from django.contrib.auth import get_user_model
from django.db.transaction import TransactionManagementError


class BaseAuthTests(ABC):
    @pytest.fixture
    def user_data(self, faker):
        def generate_user(**override):
            name = faker.name().split()
            first_name = name[0]
            last_name = name[-1]
            username = first_name + last_name
            password = ''.join([
                random.choice(string.ascii_letters)
                for _ in range(20)
            ])

            data = {
                'username': username,
                'password': password,
                'email': faker.email(),
                'first_name': first_name,
                'last_name': last_name,
            }
            data.update(override)
            return data
        
        return generate_user
    
    @pytest.fixture
    def user(self, db, user_data):
        data = user_data()
        user = get_user_model().objects.create_user(**data)

        yield user, data

        with suppress(TransactionManagementError):
            user.delete()
