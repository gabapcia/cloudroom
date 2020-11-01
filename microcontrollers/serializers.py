from rest_framework import serializers
from . import models


class PinSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Pin
        fields = '__all__'


class BoardSerializer(serializers.ModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set'
    )
    status = serializers.ChoiceField(
        choices=models.Board.Status.choices,
        source='get_status_display',
    )

    class Meta:
        model = models.Board
        fields = '__all__'
