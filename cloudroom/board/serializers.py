from rest_framework import serializers
from board import models
from board.util import model_validators


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set',
    )
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = models.Board
        fields = '__all__'
        read_only_fields = [
            'last_request',
            'allowed'
        ]


class PinSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(PinSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
    def validate(self, data):
        model_validators.pin_validator(
            status=data['status'], 
            configuration=data['configuration'], 
            from_rest=True
        )
        return data

    class Meta:
        model = models.Pin
        fields = '__all__'


class PeriodicPinSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.PeriodicPin
        fields = '__all__'
