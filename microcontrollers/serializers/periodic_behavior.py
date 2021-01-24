from rest_framework import serializers
from django.db import transaction
from celery import current_app
from cloudroom.serializers.celery import PeriodicTaskSerializer
from ..models import PeriodicPinBehavior


class PeriodicPinBehaviorSerializer(serializers.ModelSerializer):
    pin_url = serializers.HyperlinkedRelatedField(
        view_name='pin-detail',
        source='pin',
        read_only=True,
    )

    def __init__(self, *args, **kwargs):
        current_module = __package__.split('.')[0]
        current_app.loader.import_default_modules()
        tasks = list(sorted(
            name
            for name in current_app.tasks
            if name.startswith(current_module)
        ))
        self._tasks = tasks
        super().__init__(*args, **kwargs)

    def get_fields(self):
        fields = super().get_fields()
        fields['task'] = PeriodicTaskSerializer(tasks=self._tasks)
        return fields

    class Meta:
        model = PeriodicPinBehavior
        fields = '__all__'


class CreatePeriodicPinBehaviorSerializer(PeriodicPinBehaviorSerializer):
    @transaction.atomic()
    def create(self, validated_data):
        task = PeriodicTaskSerializer(
            tasks=self._tasks,
            data=validated_data['task'],
        )
        task.is_valid(raise_exception=True)
        task.save()

        data = validated_data | {'task': task.instance}
        periodic_behavior = PeriodicPinBehavior.objects.create(**data)
        return periodic_behavior


class CreateWithoutShowingPinFieldSerializer(
    CreatePeriodicPinBehaviorSerializer,
):
    pin = None

    class Meta:
        model = PeriodicPinBehavior
        exclude = ['pin']
