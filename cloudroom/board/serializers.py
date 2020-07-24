from rest_framework import serializers
from . import models


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pin
        fields = [
            'created',
            'updated',
            'board',
            'number',
            'value',
            'mode',
            'is_digital',
            'description',
        ]
        read_only_fields = ['created', 'updated']

class BoardSerializer(serializers.ModelSerializer):
    pins = PinSerializer(many=True, read_only=True, source='pin_set')
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )
    class Meta:
        model = models.Board
        fields = '__all__'
