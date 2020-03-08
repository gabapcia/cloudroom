from django.db import models
from django.core.validators import MinLengthValidator
from board.util.database import Validator
import argon2


class Board(models.Model):
    name = models.CharField(max_length=15, unique=True, db_index=True)
    status = models.BooleanField(default=False, choices=(
        (True, 'ACTIVATED'),
        (False, 'DEACTIVATED'),
    ))
    password = models.CharField(max_length=100)
    allowed = models.BooleanField(default=True)
    last_request = models.DateTimeField(null=True, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        if not self.pk:
            ph = argon2.PasswordHasher()
            self.password = ph.hash(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Board ID: #{self.pk} - {self.name}'


class Pin(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE, editable=False)
    number = models.PositiveIntegerField(db_index=True)
    status = models.CharField(max_length=4)
    mode = models.BooleanField(default=False, choices=(
        (True, 'INPUT'),
        (False, 'OUTPUT'),
    ))
    configuration = models.IntegerField(choices=(
        (0, 'DIGITAL'),
        (1, 'ANALOG'),
        (2, 'PWM'),
    ))
    description = models.TextField(max_length=256, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['number', 'board'], 
                name='pin_constraint'
            )
        ]

    def save(self, *args, **kwargs):
        Validator.status_validation(self.status, self.configuration)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'Pin #{self.number} - {self.board.name}'
