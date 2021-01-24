from rest_framework import status
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import (
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    ListModelMixin,
)
from rest_framework.response import Response
from rest_framework.decorators import action
from cloudroom.mqtt.exceptions import BrokerRequestError
from .serializers import board, pin, periodic_behavior
from .exceptions import BrokerConnectionError
from .models import Board, Pin, PeriodicPinBehavior


class BoardViewSet(ModelViewSet):
    queryset = Board.objects.all().order_by('-created')

    def get_serializer_class(self):
        return {
            'update': board.UpdateBoardSerializer,
            'partial_update': board.UpdateBoardSerializer,
            'create': board.CreateBoardSerializer,
            'validate_secret': board.SecretValidationSerializer,
            'generate_new_secret': board.UpdateSecretSerializer,
        }.get(self.action) or board.BoardSerializer

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, *args, **kwargs):
        try:
            return super().destroy(request, *args, **kwargs)
        except BrokerRequestError as e:  # pragma: no cover
            raise BrokerConnectionError from e

    @action(methods=['POST'], detail=True, url_path='validate-secret')
    def validate_secret(self, request, pk):
        serializer = board.SecretValidationSerializer(
            instance=self.get_object(),
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['PATCH'], detail=True, url_path='generate-new-secret')
    def generate_new_secret(self, request, pk):
        serializer = board.UpdateSecretSerializer(
            instance=self.get_object(),
            data={},
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'secret': serializer.secret})

    @action(methods=['GET'], detail=True)
    def pins(self, request, pk):
        serializer = pin.BasicPinInfoSerializer(
            self.get_object().pin_set.all(),
            many=True,
        )
        return Response(serializer.data)


class PinViewSet(ModelViewSet):
    queryset = Pin.objects.all().order_by('-created')

    def get_serializer_class(self):
        return {
            'update': pin.UpdatePinSerializer,
            'partial_update': pin.UpdatePinSerializer,
            'periodic_behaviors':
                periodic_behavior.PeriodicPinBehaviorSerializer,
            'create_behavior':
                periodic_behavior.CreateWithoutShowingPinFieldSerializer,
        }.get(self.action) or pin.PinSerializer

    @action(methods=['GET'], detail=True, url_path='periodic-behaviors')
    def periodic_behaviors(self, request, pk):
        data = self.get_object().periodicpinbehavior_set.all()
        serializer = periodic_behavior.PeriodicPinBehaviorSerializer(
            data,
            many=True,
            context={'request': request},
        )
        return Response(serializer.data)

    @periodic_behaviors.mapping.post
    def create_behavior(self, request, pk):
        serializer = periodic_behavior.CreateWithoutShowingPinFieldSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)
        serializer.save(pin=self.get_object())
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PeriodicPins(
    GenericViewSet,
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
):
    queryset = PeriodicPinBehavior.objects.all().order_by('-created')

    def get_serializer_class(self):
        return {
            'create': periodic_behavior.CreatePeriodicPinBehaviorSerializer,
        }.get(self.action) or periodic_behavior.PeriodicPinBehaviorSerializer
