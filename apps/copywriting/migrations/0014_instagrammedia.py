# Generated by Django 2.2 on 2022-01-01 05:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('copywriting', '0013_fileitem'),
    ]

    operations = [
        migrations.CreateModel(
            name='InstagramMedia',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('add_time', models.DateTimeField(default=django.utils.timezone.now, verbose_name='添加时间')),
                ('media_id', models.CharField(max_length=200, verbose_name='media_id')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='用户')),
            ],
            options={
                'verbose_name': 'InstagramMedia',
                'verbose_name_plural': 'InstagramMedia',
            },
        ),
    ]
