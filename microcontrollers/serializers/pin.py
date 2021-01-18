import re
from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import ValidationError
from rest_framework.validators import UniqueTogetherValidator
from ..models import Pin


class PinSerializer(ModelSerializer):
    def validate(self, data):
        if 'value' in data and 'is_digital' not in data:
            m = 'Changing the value is only allowed if the pin type is informed'
            raise ValidationError(m)
        elif 'is_digital' in data and 'value' not in data:
            m = 'Changing the pin type is only allowed if the value is informed'
            raise ValidationError(m)
        elif 'is_digital' in data and 'value' in data:
            if data['is_digital']:
                if not re.search(r'^ON|OFF$', data['value']):
                    raise ValidationError('Invalid value for digital pin')
            else:
                if not re.search(r'^\d{1,4}$', data['value']):
                    raise ValidationError('Invalid value for a non digital pin')
                elif int(data['value']) > 1023 or int(data['value']) < 0:
                    m = 'Pin value must be between 0 and 1023'
                    raise ValidationError(m)

        return data

    class Meta:
        model = Pin
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=model.objects.all(),
                fields=['number', 'board'],
            )
        ]


class UpdatePinSerializer(PinSerializer):
    def to_representation(self, instance):
        return PinSerializer(instance, context=self.context).data

    class Meta:
        model = Pin
        exclude = ['number', 'board']
