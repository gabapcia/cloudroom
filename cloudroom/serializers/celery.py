import json
from json.decoder import JSONDecodeError
from typing import Optional
from importlib import import_module
from inspect import signature
import pytz
from rest_framework import serializers
from django.conf import settings
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from rest_framework.exceptions import ValidationError


class CrontabScheduleSerializer(serializers.ModelSerializer):
    def create(self, validated_data):
        validated_data = {
            k: v
            for k, v in validated_data.items()
            if v
        }
        data = {
            'minute': '*',
            'hour': '*',
            'day_of_week': '*',
            'day_of_month': '*',
            'month_of_year': '*',
            'timezone': pytz.timezone(settings.CELERY_TIMEZONE),
        }

        data |= validated_data
        instance = CrontabSchedule.objects.get_or_create(**data)[0]
        return instance

    class Meta:
        model = CrontabSchedule
        exclude = ['timezone', 'id']


class PeriodicTaskSerializer(serializers.ModelSerializer):
    def __init__(self, tasks: Optional[list[str]] = None, *args, **kwargs):
        self._tasks = tasks or list()
        super().__init__(*args, **kwargs)

    crontab = CrontabScheduleSerializer()

    def validate(self, attrs):
        if attrs.get('kwargs'):
            try:
                task_kwargs = json.loads(attrs.get('kwargs'))
            except JSONDecodeError as e:
                raise ValidationError('kwargs is not JSON encodable') from e
        else:
            task_kwargs = {}

        module, task = attrs['task'].rsplit('.', 1)
        task_signature = signature(getattr(import_module(module), task))

        if list(task_kwargs.keys()) != list(task_signature.parameters.keys()):
            params = ', '.join(task_signature.parameters.keys())
            m = f'This task needs the following arguments: {params}'
            raise ValidationError(m)

        for arg, specs in task_signature.parameters.items():
            if not isinstance(task_kwargs[arg], specs.annotation):
                m = 'Argument "{arg}" must be of type "{type}"'.format(
                    arg=arg,
                    type=specs.annotation.__name__,
                )
                raise ValidationError(m)

        return super().validate(attrs)

    def get_fields(self):
        fields = super().get_fields()
        fields['task'] = serializers.ChoiceField(
            choices=self._tasks,
            help_text=fields['task'].help_text,
        )
        return fields

    def create(self, validated_data):
        crontab = CrontabScheduleSerializer(data=validated_data['crontab'])
        crontab.is_valid(raise_exception=True)
        crontab.save()

        data = validated_data | {'crontab': crontab.instance}
        periodic_task = PeriodicTask.objects.create(**data)
        return periodic_task

    class Meta:
        model = PeriodicTask
        fields = [
            'id',
            'name',
            'task',
            'kwargs',
            'expires',
            'one_off',
            'start_time',
            'enabled',
            'description',
            'crontab',
        ]
