from rest_framework import viewsets, status, mixins
from rest_framework.permissions import IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response

from util.serializers import PeriodicTaskSerializer
from . import models, serializers, permissions


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

    def get_serializer_class(self):
        if self.action == 'periodic':
            return lambda *args, **kwargs: (
                PeriodicTaskSerializer(app=__package__, *args, **kwargs)
            )
        else: return serializers.PinSerializer

    @action(methods=['post'], detail=True)
    def periodic(self, request, pk):
        pin = self.get_object()
        task = self.get_serializer().create(form=request.data)
        pin.periodic_behaviors.add(task)
        return Response({})
