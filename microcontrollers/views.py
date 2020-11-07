from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from . import models, serializers
from .permissions import BoardPermission


class BoardViewSet(ModelViewSet):
    queryset = models.Board.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return serializers.UpdateBoardSerializer

        return serializers.BoardSerializer

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthenticated | BoardPermission],
    )
    def pins(self, request, pk):
        board = self.get_object()
        data = [pin.basic_info() for pin in board.pin_set.all()]
        return Response(data=data)


class PinViewSet(ModelViewSet):
    queryset = models.Pin.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return serializers.UpdatePinSerializer

        return serializers.PinSerializer
