# Generated by Django 2.2 on 2022-01-04 03:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0006_auto_20211231_1338'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='pricing_tier',
            field=models.CharField(blank=True, default='free', max_length=50, verbose_name='付费方案'),
        ),
    ]