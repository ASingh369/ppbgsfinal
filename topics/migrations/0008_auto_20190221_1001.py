# Generated by Django 2.1.5 on 2019-02-21 18:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0007_pdf'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pdf',
            name='topic',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='topics.Topic', unique=True),
        ),
    ]
