# Generated by Django 2.1.5 on 2019-03-31 19:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0009_auto_20190331_1947'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklytask',
            name='end_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 31, 19, 52, 1, 278615)),
        ),
        migrations.AlterField(
            model_name='weeklytask',
            name='start_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 31, 19, 50, 51, 278615)),
        ),
    ]
