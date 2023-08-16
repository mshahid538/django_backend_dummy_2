# Generated by Django 2.2 on 2021-10-22 21:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0003_auto_20210930_2158'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='total_copy_count',
            field=models.BigIntegerField(default=0, verbose_name='复制次数'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_thumb_down_count',
            field=models.BigIntegerField(default=0, verbose_name='踩次数'),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='total_thumb_up_count',
            field=models.BigIntegerField(default=0, verbose_name='赞次数'),
        ),
    ]
