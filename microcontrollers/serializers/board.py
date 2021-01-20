import string
import random
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from cloudroom.mqtt.exceptions import BrokerRequestError
from ..exceptions import BrokerConnectionError
from ..models import Board


class BaseSerializer(serializers.ModelSerializer):
    SECRET_SIZE = 50

    def generate_secret(self) -> str:
        c = ''.join([string.ascii_letters, string.punctuation, string.digits])
        secret = random.choices(c, k=BaseSerializer.SECRET_SIZE)
        secret = ''.join(secret)

        return secret

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if 'status' in data:
            data['status'] = instance.get_status_display()

        return data


class BoardSerializer(BaseSerializer):
    pins = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='pin-detail',
        source='pin_set'
    )

    class Meta:
        model = Board
        exclude = ['secret']


class CreateBoardSerializer(BaseSerializer):
    def create(self, validated_data):
        self.secret = self.generate_secret()
        data = dict(**validated_data, secret=self.secret)

        try:
            board = Board.objects.create(**data)
        except BrokerRequestError as e:  # pragma: no cover
            raise BrokerConnectionError from e

        return board

    def to_representation(self, instance):
        data = {
            'id': instance.pk,
            'name': instance.name,
            'secret': self.secret,
        }
        return data

    class Meta:
        model = Board
        fields = ['name', 'status']


class UpdateBoardSerializer(BoardSerializer):
    def to_representation(self, instance):
        return BoardSerializer(instance, context=self.context).data

    class Meta:
        model = Board
        exclude = ['secret', 'name']


class SecretValidationSerializer(BaseSerializer):
    def validate_secret(self, value):
        match = self.instance.verify_secret(value)
        if not match:
            raise ValidationError('Invalid secret')

        return value

    class Meta:
        model = Board
        fields = ['secret']


class UpdateSecretSerializer(BaseSerializer):
    def update(self, instance, validated_data):
        self.secret = self.generate_secret()

        try:
            instance.update_secret(self.secret)
        except BrokerRequestError as e:  # pragma: no cover
            raise BrokerConnectionError from e

        return instance

    class Meta:
        model = Board
        fields = []
