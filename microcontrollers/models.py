from argon2 import PasswordHasher
from argon2.exceptions import (
    HashingError,
    VerificationError,
    VerifyMismatchError,
)
from .exceptions import HashSecretError
from django.db import models
from django.core.validators import MinLengthValidator


class Board(models.Model):
    class Status(models.IntegerChoices):
        DEACTIVATED = 1
        ACTIVATED = 2
        BLOCKED = 3

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=15, unique=True)
    secret = models.CharField(max_length=255)
    status = models.IntegerField(
        choices=Status.choices,
        default=Status.DEACTIVATED,
    )

    def hash_secret(self, secret: str) -> str:
        ph = PasswordHasher()
        try:
            hash = ph.hash(secret)
        except HashingError:
            raise HashSecretError

        return hash

    def verify_secret(self, secret: str) -> bool:
        ph = PasswordHasher()
        try:
            ph.verify(self.secret, secret)
        except VerifyMismatchError:
            return False

        if ph.check_needs_rehash(self.secret):
            self.secret = self.hash_secret(secret=secret)
            self.save()

        return True

    def save(self, *args, **kwargs):
        if not self.pk:
            self.secret = self.hash_secret(secret=self.secret)

        super().save(*args, **kwargs)

    def __str__(self):
        return f'Board ID: #{self.pk} - {self.name}'

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['status']),
        ]


class Pin(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    board = models.ForeignKey(Board, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    value = models.CharField(max_length=4)
    is_digital = models.BooleanField(default=True)
    description = models.CharField(max_length=512, null=True, blank=True)

    def basic_info(self) -> dict:
        return {
            'number': self.number,
            'value': self.value,
            'is_digital': self.is_digital,
        }

    class Meta:
        indexes = [
            models.Index(fields=['created']),
            models.Index(fields=['updated']),
            models.Index(fields=['number']),
            models.Index(fields=['value']),
            models.Index(fields=['is_digital']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'board'],
                name='pin_constraint'
            ),
            models.CheckConstraint(
                check=(
                    models.Q(value__regex=r'^ON|OFF$', is_digital=True) |
                    models.Q(value__regex=r'^\d{1,4}$', is_digital=False)
                ),
                name='pin_value_by_type',
            ),
        ]
