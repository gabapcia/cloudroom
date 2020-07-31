import json, pytz
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.db import transaction
from datetime import datetime
from django_celery_beat.models import PeriodicTask, CrontabSchedule
from timezone_field import TimeZoneField
from celery import current_app


class CrontabScheduleSerializer(serializers.ModelSerializer):
    timezone = serializers.SerializerMethodField()

    def get_timezone(self, obj): return str(obj.timezone)

    class Meta:
        model = CrontabSchedule
        fields = '__all__'
        read_only_fields = ['timezone']

class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleSerializer()

    def __init__(self, app=None, *args, **kwargs):
        super(PeriodicTaskSerializer, self).__init__(*args, **kwargs)
        if not app:
            app = kwargs['context']['view'].__class__.__module__.split('.')[0]
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
            'id',
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
        read_only_fields = ['id', 'kwargs', 'queue']

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
                ('*' if field != 'timezone' else settings.CELERY_TIMEZONE)
            )
            for field in fields
        }

    def _get_periodic_data(self, form):
        fields = [
            ('name', str, ''),
            ('one_off', bool, False),
            ('start_time', str, None),
            ('enabled', bool, True),
            ('description', str, ''),
            ('task', str, ''),
        ]

        data = {}
        for field, field_type, default in fields:
            value = form.get(field, '')
            if type(value) is not field_type: value = default
            if field == 'start_time' and not value: value = default
            data[field] = value

        if not data['task']: raise ValidationError(_('"task" is required'))
        if not data['name']: raise ValidationError(_('"name" is required'))

        return data

    def _manage_kwargs(self, current, new):
        new_keys = set(new.keys()) - set(current.keys())
        result = {key: new[key] for key in new_keys}
        for key, value in current.items():
            if type(value) is not dict:
                result[key] = value + new.get(key, type(value)())
            else: result[key] = {**value, **new.get(key, {})}
        return result

    def create(self, form, task_kwargs):
        crontab = self._get_crontab_data(form=form)
        periodic = self._get_periodic_data(form=form)
        
        # TODO: handle validation
        crontab = CrontabSchedule.objects.get_or_create(**crontab)[0]
        periodic['crontab'] = crontab
            
        with transaction.atomic():
            try:
                task = PeriodicTask.objects.select_for_update().get(**periodic)
                task.kwargs = self._manage_kwargs(
                    current=json.loads(task.kwargs), 
                    new=task_kwargs
                )
                task.save()
            except PeriodicTask.DoesNotExist:
                task = PeriodicTask.objects.create(
                    kwargs=json.dumps(task_kwargs),
                    **periodic
                )

        return task

    @transaction.atomic
    def delete_kwargs(self, pk, **kwargs):
        task = PeriodicTask.objects.select_for_update().get(pk=pk)
        task_kwargs = json.loads(task.kwargs)
        
        new_kwargs = {}
        for k, v in kwargs.items():
            if type(v) is not list: 
                raise ValidationError(_('only list is supported'))

            try:
                for item in v: task_kwargs[k].remove(item)
            except:
                raise ValidationError(_('invalid value to remove'))

            if not task_kwargs[k]: continue
            else: new_kwargs[k] = task_kwargs[k]
        
        if not new_kwargs: task.delete()
        else:
            task.kwargs = json.dumps(new_kwargs)
            task.save()
