from argon2 import PasswordHasher
from argon2.exceptions import HashingError, VerifyMismatchError
from django.db import models, transaction
from cloudroom.mqtt import Manager as MQTTManager
from .exceptions import HashSecretError
from .validators import validate_pin_value


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

    def _hash_secret(self, secret: str) -> str:
        ph = PasswordHasher()
        try:
            hash = ph.hash(secret)
        except HashingError as e:  # pragma: no cover
            raise HashSecretError from e

        return hash

    def verify_secret(self, secret: str) -> bool:
        ph = PasswordHasher()
        try:
            ph.verify(self.secret, secret)
        except VerifyMismatchError:
            return False

        if ph.check_needs_rehash(self.secret):  # pragma: no cover
            self.secret = self._hash_secret(secret=secret)
            self.save()

        return True

    @transaction.atomic()
    def update_secret(self, secret: str) -> None:
        manager = MQTTManager()
        manager.update_user_password(username=self.name, new_password=secret)
        self.secret = self._hash_secret(secret)
        self.save()

    @transaction.atomic()
    def save(self, *args, **kwargs):
        if not self.pk:
            manager = MQTTManager()
            manager.create_user(username=self.name, password=self.secret)
            manager.grant_user_permissions(username=self.name)
            self.secret = self._hash_secret(secret=self.secret)

        super().save(*args, **kwargs)

    @transaction.atomic()
    def delete(self, **kwargs) -> tuple[int, dict[str, int]]:
        manager = MQTTManager()
        manager.delete_user(username=self.name)
        return super().delete(**kwargs)

    def __str__(self):  # pragma: no cover
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
    name = models.CharField(max_length=15)
    number = models.PositiveIntegerField()
    value = models.CharField(max_length=4, validators=[validate_pin_value])
    is_digital = models.BooleanField(default=True)
    description = models.CharField(max_length=512, null=True, blank=True)

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
                name='unique pin number per board',
            ),
            models.UniqueConstraint(
                fields=['name', 'board'],
                name='Unique pin name per board',
            ),
            models.CheckConstraint(
                check=(
                    models.Q(value__regex=r'^ON|OFF$', is_digital=True) |
                    models.Q(value__regex=r'^\d{1,4}$', is_digital=False)
                ),
                name='Check pin value by type',
            ),
        ]
