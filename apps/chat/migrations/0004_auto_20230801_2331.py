# Generated by Django 2.2 on 2023-08-02 06:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0003_convertedfilemodel_downloadable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='convertedfilemodel',
            name='downloadable',
            field=models.BooleanField(default=True),
        ),
    ]
