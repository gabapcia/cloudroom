from rest_framework.viewsets import ReadOnlyModelViewSet
from . import serializers, models


class MessageViewSet(ReadOnlyModelViewSet):
    queryset = models.Message.objects.all().order_by('-created')
    serializer_class = serializers.MessageSerializer
