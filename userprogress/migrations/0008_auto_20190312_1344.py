# Generated by Django 2.1.5 on 2019-03-12 13:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprogress', '0007_userlastlocation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userlastlocation',
            name='location',
            field=models.CharField(choices=[('notes', 'Notes'), ('videos', 'Videos'), ('quiz', 'Quiz'), ('challenges', 'Challenges')], default='notes', max_length=10),
        ),
    ]