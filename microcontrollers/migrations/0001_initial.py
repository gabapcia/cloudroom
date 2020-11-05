# Generated by Django 3.1.3 on 2020-11-03 23:46

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Board',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=15, unique=True)),
                ('secret', models.CharField(max_length=255)),
                ('status', models.IntegerField(choices=[(1, 'Deactivated'), (2, 'Activated'), (3, 'Blocked')], default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Pin',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('number', models.PositiveIntegerField()),
                ('value', models.CharField(max_length=4)),
                ('is_digital', models.BooleanField(default=True)),
                ('description', models.CharField(blank=True, max_length=512, null=True)),
                ('board', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='microcontrollers.board')),
            ],
        ),
        migrations.AddIndex(
            model_name='board',
            index=models.Index(fields=['created'], name='microcontro_created_f475de_idx'),
        ),
        migrations.AddIndex(
            model_name='board',
            index=models.Index(fields=['updated'], name='microcontro_updated_e851b0_idx'),
        ),
        migrations.AddIndex(
            model_name='board',
            index=models.Index(fields=['status'], name='microcontro_status_072ca4_idx'),
        ),
        migrations.AddIndex(
            model_name='pin',
            index=models.Index(fields=['created'], name='microcontro_created_113565_idx'),
        ),
        migrations.AddIndex(
            model_name='pin',
            index=models.Index(fields=['updated'], name='microcontro_updated_ee8942_idx'),
        ),
        migrations.AddIndex(
            model_name='pin',
            index=models.Index(fields=['number'], name='microcontro_number_66305c_idx'),
        ),
        migrations.AddIndex(
            model_name='pin',
            index=models.Index(fields=['value'], name='microcontro_value_7ccb55_idx'),
        ),
        migrations.AddIndex(
            model_name='pin',
            index=models.Index(fields=['is_digital'], name='microcontro_is_digi_2bf53c_idx'),
        ),
        migrations.AddConstraint(
            model_name='pin',
            constraint=models.UniqueConstraint(fields=('number', 'board'), name='pin_constraint'),
        ),
        migrations.AddConstraint(
            model_name='pin',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('is_digital', True), ('value__regex', '^ON|OFF$')), models.Q(('is_digital', False), ('value__regex', '^\\d{1,4}$')), _connector='OR'), name='pin_value_by_type'),
        ),
    ]
