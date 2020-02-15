from rest_framework import viewsets
from orders import serializers, models


class CorreiosViewSet(viewsets.ModelViewSet):
    queryset = models.Correios.objects.order_by('-id')
    serializer_class = serializers.CorreiosSerializer


class CorreiosInfoViewSet(viewsets.ModelViewSet):
    queryset = models.CorreiosInfo.objects.order_by('-id')
    serializer_class = serializers.CorreiosInfoSerializer

