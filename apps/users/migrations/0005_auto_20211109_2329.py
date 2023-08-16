# Generated by Django 2.2 on 2021-11-10 07:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_auto_20211022_2159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='address',
            field=models.CharField(blank=True, default='', max_length=100, verbose_name='地址'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('male', '男'), ('female', '女')], max_length=6, verbose_name='性别'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, default='default.jpg', upload_to='head_image/%Y/%m', verbose_name='用户头像'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='mobile',
            field=models.CharField(blank=True, max_length=11, verbose_name='电话号码'),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='nick_name',
            field=models.CharField(blank=True, default='', max_length=50, verbose_name='昵称'),
        ),
    ]