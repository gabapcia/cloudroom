from rest_framework import viewsets
from board import models, serializers


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all().order_by('name')
    serializer_class = serializers.BoardSerializer


class PinViewSet(viewsets.ModelViewSet):
    queryset = models.Pin.objects.all().order_by('number')
    serializer_class = serializers.PinSerializer
