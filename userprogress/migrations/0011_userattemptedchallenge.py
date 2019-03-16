# Generated by Django 2.1.5 on 2019-03-15 18:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('challenges', '0007_hint'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('userprogress', '0010_auto_20190313_1427'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserAttemptedChallenge',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('start_datetime', models.DateTimeField(blank=True, default=datetime.datetime.now)),
                ('points', models.IntegerField(default=0)),
                ('challenge', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='challenges.Challenge')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
