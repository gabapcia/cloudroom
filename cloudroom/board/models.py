from django.db import models
from board.util.database import Validator


class Board(models.Model):
    name = models.CharField(max_length=15, unique=True, db_index=True)
    status = models.BooleanField(default=False, choices=(
        (True, 'ACTIVATED'),
        (False, 'DEACTIVATED'),
    ))

    def __str__(self):
        return f'{self.name}'


class Pin(models.Model):
    board = models.ForeignKey('Board', on_delete=models.CASCADE)
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
