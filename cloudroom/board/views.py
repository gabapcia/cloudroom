from rest_framework import viewsets, status, response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from board import models, serializers
from board.util import request_handler


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all().order_by('name')
    serializer_class = serializers.BoardSerializer
  

class PinViewSet(viewsets.ModelViewSet):
    queryset = models.Pin.objects.all().order_by('number')
    serializer_class = serializers.PinSerializer
    
    @action(
        detail=False, 
        methods=['GET'], 
        permission_classes=[AllowAny],
    )
    def status(self, request):
        return request_handler.board_pin_list(
            request=request
        )

class PeriodicPinViewSet(viewsets.ModelViewSet):
    queryset = models.PeriodicPin.objects.all().order_by('-id')
    serializer_class = serializers.PeriodicPinSerializer
