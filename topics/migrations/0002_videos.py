# Generated by Django 2.1.5 on 2019-02-13 08:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Videos',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=300)),
                ('channelName', models.CharField(max_length=400)),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='topics.Topic')),
            ],
        ),
    ]
