from rest_framework import serializers
from . import models


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pin
        fields = '__all__'
        read_only_fields = ['created', 'updated']


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
    status_display = serializers.ChoiceField(
        choices=models.Board.Status.choices,
        source='get_status_display',
        read_only=True
    )

    class Meta:
        model = models.Board
        fields = '__all__'
