# Generated by Django 2.2 on 2022-01-05 20:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copywriting', '0015_auto_20211231_2237'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrammedia',
            name='caption',
            field=models.CharField(default='', max_length=500, null=True, verbose_name='caption'),
        ),
    ]
