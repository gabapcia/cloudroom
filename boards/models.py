import argon2
from django.db import models
from django.core.validators import MinLengthValidator
from .core.validators import validate_pin_value


class Board(models.Model):
    class Status(models.IntegerChoices):
        DEACTIVATED = 1
        ACTIVATED = 2
        BLOCKED = 3

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    name = models.CharField(max_length=15, unique=True)
    status = models.IntegerField(choices=Status.choices)
    password = models.TextField(validators=[MinLengthValidator(12)])

    def save(self, *args, **kwargs):
        if not self.pk:
            ph = argon2.PasswordHasher()
            self.password = ph.hash(self.password)
        super().save(*args, **kwargs)

    def verify_password(self, password):
        ph = argon2.PasswordHasher()
        ph.verify(self.password, password)

        if ph.check_needs_rehash(self.password):
            self.password = ph.hash(password)
            self.save()

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
    value = models.CharField(
        max_length=3,
        validators=[validate_pin_value]
    )
    is_digital = models.BooleanField(default=True)
    description = models.CharField(max_length=512, null=True)

    def operation_info(self):
        return {'number': self.number, 'value': self.value}

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
                    models.Q(value__regex=r'ON|OFF', is_digital=True) |
                    models.Q(value__regex=r'^\d+$', is_digital=False)
                ),
                name='pin_value_by_type',
            ),
        ]
