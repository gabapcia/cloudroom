from rest_framework import serializers
from django_celery_beat.models import PeriodicTask

from util.serializers import PeriodicTaskSerializer
from . import models


class PinSerializer(serializers.HyperlinkedModelSerializer):
    periodic_behaviors = serializers.SlugRelatedField(
        read_only=True, 
        slug_field='name',
        many=True
    )

    class Meta:
        model = models.Pin
        fields = '__all__'
        read_only_fields = ['created', 'updated', 'periodic_behaviors']

class BoardSerializer(serializers.HyperlinkedModelSerializer):
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
        source='get_status_display'
    )

    class Meta:
        model = models.Board
        fields = '__all__'
