from rest_framework import serializers
from orders import models


class CorreiosSerializer(serializers.HyperlinkedModelSerializer):
    details = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='correiosinfo-detail',
        source='correiosinfo_set'
    )

    class Meta:
        model = models.Correios
        fields = '__all__'


class CorreiosInfoSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.CorreiosInfo
        fields = '__all__'

