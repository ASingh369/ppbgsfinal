# Generated by Django 2.1.5 on 2019-03-25 14:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprogress', '0017_level'),
    ]

    operations = [
        migrations.AddField(
            model_name='level',
            name='progress',
            field=models.IntegerField(default=0),
        ),
    ]
