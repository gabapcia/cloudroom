import re
from rest_framework import serializers
from . import models


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pin
        fields = '__all__'
        read_only_fields = ['created', 'updated', 'periodic_behaviors']

class BoardSerializer(serializers.ModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True, 
        read_only=True,
        view_name='pin-detail',
        source='pin_set'
    )
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = models.Board
        fields = '__all__'
