# Generated by Django 2.1.5 on 2019-02-21 17:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('topics', '0006_auto_20190213_0949'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pdf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='pdfs/%Y/%m/%d/')),
                ('topic', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='topics.Topic')),
            ],
        ),
    ]
