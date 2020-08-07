from rest_framework import viewsets
from orders import serializers, models


class CorreiosViewSet(viewsets.ModelViewSet):
    queryset = models.Correios.objects.order_by('-updated')
    serializer_class = serializers.CorreiosSerializer
