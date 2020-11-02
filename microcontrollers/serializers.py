import re
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from . import models


class PinSerializer(serializers.ModelSerializer):
    def validate(self, data):
        if data['is_digital']:
            if not re.search(r'^ON|OFF$', data['value']):
                raise ValidationError('Invalid value for digital pin')
        else:
            if not re.search(r'^\d{1,4}$', data['value']):
                raise ValidationError('Invalid value for a non digital pin')

        return data

    class Meta:
        model = models.Pin
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['number', 'board'],
            )
        ]


class BoardSerializer(serializers.ModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set'
    )
    status_display = serializers.ChoiceField(
        choices=models.Board.Status.choices,
        source='get_status_display',
        read_only=True,
    )

    class Meta:
        model = models.Board
        fields = '__all__'
