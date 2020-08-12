from rest_framework import serializers
from . import models


class ChristineResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ChristineResponse
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    response = ChristineResponseSerializer(source='christineresponse')

    class Meta:
        model = models.Message
        fields = '__all__'
