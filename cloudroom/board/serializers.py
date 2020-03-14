from rest_framework import serializers
from board import models


class BoardSerializer(serializers.HyperlinkedModelSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set',
    )
    last_request = serializers.ReadOnlyField()
    allowed = serializers.ReadOnlyField()
    password = serializers.CharField(
        write_only=True, 
        style={'input_type': 'password'}
    )

    class Meta:
        model = models.Board
        fields = '__all__'


class PinSerializer(serializers.HyperlinkedModelSerializer):
    def __init__(self, *args, **kwargs):
        fields = kwargs.pop('fields', None)

        super(PinSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields)
            for field_name in existing - allowed:
                self.fields.pop(field_name)
    
    class Meta:
        model = models.Pin
        fields = '__all__'
