import re
from rest_framework import serializers
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from . import models


class PinSerializer(serializers.ModelSerializer):    
    def validate(self, data):
        if 'value' in data and 'is_digital' not in data:
            raise ValidationError(
                'Changing the value is only allowed if the pin type is informed'
            )
        elif 'is_digital' in data and 'value' not in data:
            raise ValidationError(
                'Changing the pin type is only allowed if the value is informed'
            )
        elif 'is_digital' in data and 'value' in data:
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


class UpdatePinSerializer(PinSerializer):
    def to_representation(self, instance):
        return PinSerializer(instance).data

    class Meta:
        model = models.Pin
        exclude = ['number', 'board']


class BoardSerializer(serializers.ModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set'
    )

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'status' in data:
            data['status'] = instance.get_status_display()

        return data

    class Meta:
        model = models.Board
        fields = '__all__'
        extra_kwargs = {
            'secret': {
                'write_only': True,
                'style': {'input_type': 'password'}
            }
        }


class UpdateBoardSerializer(BoardSerializer):
    def to_representation(self, instance):
        return BoardSerializer(instance).data

    class Meta:
        model = models.Board
        exclude = ['secret', 'name']
