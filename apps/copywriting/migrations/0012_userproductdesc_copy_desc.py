# Generated by Django 2.2 on 2021-12-17 05:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('copywriting', '0011_userproductdesc_edited_result_link'),
    ]

    operations = [
        migrations.AddField(
            model_name='userproductdesc',
            name='copy_desc',
            field=models.BooleanField(blank=True, default=False, verbose_name='复制'),
        ),
    ]
