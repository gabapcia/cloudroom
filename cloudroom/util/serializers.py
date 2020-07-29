from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import datetime
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from timezone_field import TimeZoneField
from celery import current_app


class CrontabScheduleSerializer(serializers.ModelSerializer):
    timezone = serializers.ChoiceField(choices=TimeZoneField.CHOICES)

    class Meta:
        model = CrontabSchedule
        fields = '__all__'

class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleSerializer()

    def __init__(self, app, *args, **kwargs):
        super(PeriodicTaskSerializer, self).__init__(*args, **kwargs)
        
        current_app.loader.import_default_modules()
        tasks = sorted(
            name 
            for name in current_app.tasks 
            if not name.startswith('celery.') and name.startswith(f'{app}.')
        )
        tasks_name = map(
            lambda t: ' '.join(t.split('.')[-1].split('_')).title(),
            tasks
        )
        self.fields['task'] = serializers.ChoiceField(
            choices=(('', ''), ) + tuple(zip(tasks, tasks_name))
        )

    class Meta:
        model = PeriodicTask
        fields = [
            'crontab',
            'task',
            'name',
            'task',
            'kwargs',
            'queue',
            'one_off',
            'start_time',
            'enabled',
            'description',
        ]
        read_only_fields = ['kwargs', 'queue']

    def _get_crontab_data(self, form):
        fields = [
            'timezone',
            'minute',
            'hour',
            'day_of_week',
            'day_of_month',
            'month_of_year',
        ]
        
        return {
            field: (
                form.get('crontab', {}).get(field, '') or 
                form.get(f'crontab.{field}', '') or 
                ('*' if field != 'timezone' else 'America/Sao_Paulo')
            )
            for field in fields
        }

    def _get_periodic_data(self, form):
        fields = [
            ('name', str, ''),
            ('one_off', bool, False),
            ('start_time', str, datetime.now().isoformat()),
            ('enabled', bool, True),
            ('description', str, ''),
            ('task', str, ''),
        ]

        data = {}
        for field, field_type, default in fields:
            value = form.get(field, '')
            if type(value) is not field_type: value = default
            data[field] = value

        if not data['task']: raise ValidationError(_('"task" is required'))

        return data

    def create(self, form):
        crontab = self._get_crontab_data(form=form)
        periodic = self._get_periodic_data(form=form)

        # TODO: handle validation
        periodic['crontab'] = \
            CrontabSchedule.objects.get_or_create(**crontab)[0]
        return PeriodicTask.objects.get_or_create(**periodic)[0]
