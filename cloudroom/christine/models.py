from django.db import models
from django.conf import settings


class Message(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    text = models.TextField()
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    class Meta:
        indexes = [
            models.Index(fields=['created']),
        ]


class ChristineResponse(models.Model):
    class CommandType(models.IntegerChoices):
        REQUEST = 1
        RESULT = 2
        ERROR = 3

    message = models.OneToOneField(
        Message,
        on_delete=models.CASCADE,
        primary_key=True
    )
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    command_type = models.IntegerField(choices=CommandType.choices)
    text = models.TextField()
    content = models.JSONField(null=True)

    class Meta:
        indexes = [
            models.Index(fields=['created']),
        ]
