# Generated by Django 2.2 on 2022-01-05 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copywriting', '0016_auto_20220105_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instagrammedia',
            name='caption',
            field=models.CharField(blank=True, default='', max_length=500, null=True, verbose_name='caption'),
        ),
    ]
