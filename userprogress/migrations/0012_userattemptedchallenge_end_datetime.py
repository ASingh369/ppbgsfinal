# Generated by Django 2.1.5 on 2019-03-15 18:31

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprogress', '0011_userattemptedchallenge'),
    ]

    operations = [
        migrations.AddField(
            model_name='userattemptedchallenge',
            name='end_datetime',
            field=models.DateTimeField(blank=True, default=datetime.datetime.now),
        ),
    ]