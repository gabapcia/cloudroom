# Generated by Django 3.0.4 on 2020-03-08 19:17

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('board', '0004_board_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='board',
            name='password',
            field=models.CharField(max_length=100, validators=[django.core.validators.MinLengthValidator(8)]),
        ),
    ]
