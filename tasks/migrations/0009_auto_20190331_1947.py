# Generated by Django 2.1.5 on 2019-03-31 19:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('tasks', '0008_auto_20190331_1946'),
    ]

    operations = [
        migrations.AlterField(
            model_name='weeklytask',
            name='end_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2019, 3, 31, 19, 49, 4, 188440)),
        ),
    ]
