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
        if 'periodic' in self.action: return PeriodicTaskSerializer
        else: return serializers.PinSerializer

    @action(
        detail=True, 
        methods=['post', 'delete'], 
        url_path='periodic/?(?P<task_pk>[^/.]+)?'
    )
    def periodic(self, request, pk, task_pk=None):
        if request.method.lower() == 'delete':
            if not task_pk: 
                return Response(
                    {'detail': 'Task pk not provied'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            pin = self.get_object()
            if not pin.periodic_behaviors.filter(pk=task_pk).exists():
                return Response(
                    {'detail': 'Invalid task'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            pin.periodic_behaviors.remove(task_pk)
            self.get_serializer().delete_kwargs(pk=task_pk, pins=[pin.pk])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            pin = self.get_object()
            task = self.get_serializer().create(
                form=request.data,
                task_kwargs={'pins': [pin.pk]}
            )
            pin.periodic_behaviors.add(task)

            return Response(
                self.get_serializer(task).data, 
                status=status.HTTP_201_CREATED
            )

    @periodic.mapping.get
    def list_periodic(self, request, pk):
        periodic_behaviors = self.get_object().periodic_behaviors
        return Response(self.get_serializer(periodic_behaviors, many=True).data)
