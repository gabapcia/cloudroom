from rest_framework import viewsets
from . import models, serializers


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all()
    serializer_class = serializers.BoardSerializer

class PinViewSet(viewsets.ModelViewSet):
    queryset = models.Pin.objects.all()
    serializer_class = serializers.PinSerializer
