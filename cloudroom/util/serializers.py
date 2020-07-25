from django_celery_beat.models import PeriodicTask, CrontabSchedule


class CrontabScheduleSerializer(serializers.ModelSerializer):
    timezone = serializers.SerializerMethodField()

    def get_timezone(self, obj): return str(obj.timezone)
    
    class Meta:
        model = CrontabSchedule
        fields = '__all__'

class PeriodicTaskSerializer(serializers.ModelSerializer):
    crontab = CrontabScheduleSerializer()
    
    class Meta:
        model = PeriodicTask
        fields = [
            'crontab',
            'name',
            'task',
            'kwargs',
            'queue',
            'one_off',
            'start_time',
            'enabled',
            'description',
        ]
        read_only_fields = ['task', 'kwargs', 'queue']
