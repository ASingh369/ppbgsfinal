# Generated by Django 2.1.5 on 2019-02-13 17:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0005_quiz'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Quiz',
            new_name='Question',
        ),
    ]
