# Generated by Django 2.2 on 2023-08-02 06:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0002_convertedfilemodel_originalfilemodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='convertedfilemodel',
            name='downloadable',
            field=models.BooleanField(default=False),
        ),
    ]