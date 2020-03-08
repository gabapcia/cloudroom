from rest_framework import viewsets, status, response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from board import models, serializers
from board.util import request_handler


class BoardViewSet(viewsets.ModelViewSet):
    queryset = models.Board.objects.all().order_by('name')
    serializer_class = serializers.BoardSerializer

    @action(
        detail=False, 
        methods=['POST'], 
        permission_classes=[AllowAny],
    )
    def auth(self, request):
        return request_handler.validate_board(
            body=request.data
        )
  

class PinViewSet(viewsets.ModelViewSet):
    queryset = models.Pin.objects.all().order_by('number')
    serializer_class = serializers.PinSerializer
    
    @action(
        detail=False, 
        methods=['GET'], 
        permission_classes=[AllowAny],
    )
    def status(self, request):
        if 'board-token' not in request.headers:
            return response.Response(
                data={'detail': 'Authentication credentials were not provided'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return request_handler.board_pin_list(
            token=request.headers['board-token']
        )
