# Generated by Django 3.1.5 on 2021-01-23 20:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('django_celery_beat', '0015_edit_solarschedule_events_choices'),
        ('microcontrollers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PeriodicPinBehavior',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('pin', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microcontrollers.pin')),
                ('task', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='django_celery_beat.periodictask')),
            ],
        ),
        migrations.AddIndex(
            model_name='periodicpinbehavior',
            index=models.Index(fields=['created'], name='microcontro_created_33a912_idx'),
        ),
        migrations.AddIndex(
            model_name='periodicpinbehavior',
            index=models.Index(fields=['updated'], name='microcontro_updated_935e0b_idx'),
        ),
    ]