from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from . import models, serializers
from .core import permissions


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all()
    serializer_class = serializers.BoardSerializer

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAdminUser|permissions.BoardPermission],
    )
    def pins(self, request, pk):
        board = self.get_object()
        data = [pin.operation_info() for pin in board.pin_set.iterator()]
        return Response(data=data)

class PinViewSet(viewsets.ModelViewSet):
    queryset = models.Pin.objects.all()
    serializer_class = serializers.PinSerializer