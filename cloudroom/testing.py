from abc import ABC
from faker import Faker
import pytest


class BaseTest(ABC):
    @pytest.fixture(scope='class')
    def faker(self):
        faker = Faker()
        return faker
