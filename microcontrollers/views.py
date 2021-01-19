from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.decorators import action
from . import serializers
from .models import Board, Pin


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all()

    def get_serializer_class(self):
        return {
            'update': serializers.UpdateBoardSerializer,
            'partial_update': serializers.UpdateBoardSerializer,
            'create': serializers.CreateBoardSerializer,
            'validate_secret': serializers.SecretValidationSerializer,
            'generate_new_secret': serializers.UpdateSecretSerializer,
        }.get(self.action) or serializers.BoardSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=True, url_path='validate-secret')
    def validate_secret(self, request, pk):
        serializer = serializers.SecretValidationSerializer(
            instance=self.get_object(),
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PATCH'], detail=True, url_path='generate-new-secret')
    def generate_new_secret(self, request, pk):
        serializer = serializers.UpdateSecretSerializer(
            instance=self.get_object(),
            data={},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'secret': serializer.secret})

    @action(methods=['GET'], detail=True)
    def pins(self, request, pk):
        board = self.get_object()
        serializer = serializers.BasicPinInfoSerializer(
            board.pin_set.all(),
            many=True,
        )
        return Response(serializer.data)


class PinViewSet(ModelViewSet):
    queryset = Pin.objects.all()

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return serializers.UpdatePinSerializer

        return serializers.PinSerializer
