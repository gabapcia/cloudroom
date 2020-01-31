from rest_framework import serializers
from board import models


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    pin_set = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail'
    )

    class Meta:
        model = models.Board
        fields = '__all__'


class PinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Pin
        fields = '__all__'
