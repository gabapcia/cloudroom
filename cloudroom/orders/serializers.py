from rest_framework import serializers
from orders import models


class CorreiosInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.CorreiosInfo
        fields = '__all__'

class CorreiosSerializer(serializers.ModelSerializer):
    details = CorreiosInfoSerializer(
        read_only=True, 
        many=True, 
        source='correiosinfo_set'
    )

    class Meta:
        model = models.Correios
        fields = '__all__'
        read_only_fields = [
            'created',
            'updated',
            'delivered',
            'last_update',
            'cpf_registered',
        ]
