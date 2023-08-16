from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

GENDER_CHOICES = (
    ("male", "男"),
    ("female", "女")
)


class BaseModel(models.Model):
    add_time = models.DateTimeField(default=timezone.now, verbose_name="添加时间")

    class Meta:
        abstract = True


class UserProfile(AbstractUser):
    nick_name = models.CharField(
        max_length=50, verbose_name="昵称", default="", blank=True)
    birthday = models.DateField(verbose_name="生日", null=True, blank=True)
    gender = models.CharField(
        verbose_name="性别",
        choices=GENDER_CHOICES,
        max_length=6,
        blank=True)
    address = models.CharField(
        max_length=100, verbose_name="地址", default="", blank=True)
    mobile = models.CharField(max_length=11, verbose_name="电话号码", blank=True)
    image = models.ImageField(
        verbose_name="用户头像",
        upload_to="head_image/%Y/%m",
        default="default.jpg",
        blank=True)
    trial_count = models.IntegerField(default=5, verbose_name='试用次数')
    total_copy_count = models.BigIntegerField(default=0, verbose_name='复制次数')
    total_thumb_up_count = models.BigIntegerField(
        default=0, verbose_name='赞次数')
    total_thumb_down_count = models.BigIntegerField(
        default=0, verbose_name='踩次数')
    ig_id = models.CharField(default="", blank=True,
                             max_length=100, verbose_name='Instagram ID')
    ig_token = models.CharField(
        default="", blank=True, max_length=200, verbose_name='Instagram token')
    pricing_tier = models.CharField(
        max_length=50, verbose_name="付费方案", default="free", blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name

    def unread_nums(self):
        # 未读消息数量
        return self.usermessage_set.filter(has_read=False).count()

    def __str__(self):
        if self.nick_name:
            return self.nick_name
        else:
            return self.username
