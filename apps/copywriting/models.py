from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser

from apps.users.models import BaseModel

UserProfile = get_user_model()


class UserProductDesc(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="用户")
    product_name = models.CharField(max_length=200, verbose_name="产品名称")
    description = models.CharField(max_length=600, verbose_name="描述")
    product_type = models.CharField(
        max_length=200, verbose_name="产品类型", default='')
    result_link = models.URLField(max_length=200, verbose_name="结果")
    edited_result_link = models.URLField(
        max_length=200, verbose_name="编辑结果", blank=True)
    thumb_up = models.BooleanField(default=False, verbose_name="赞", blank=True)
    thumb_down = models.BooleanField(
        default=False, verbose_name="踩", blank=True)
    copy_desc = models.BooleanField(
        default=False, verbose_name="复制", blank=True)

    class Meta:
        verbose_name = "用户产品描述"
        verbose_name_plural = verbose_name

    def __str__(self):
        return "{product_name}_{description}".format(
            product_name=self.product_name, description=self.description)


class FileItem(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, default=1)
    name = models.CharField(max_length=120, null=True, blank=True)
    path = models.TextField(blank=True, null=True)
    size = models.BigIntegerField(default=0)
    file_type = models.CharField(max_length=120, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    uploaded = models.BooleanField(default=False)
    active = models.BooleanField(default=True)

    @property
    def title(self):
        return str(self.name)

    class Meta:
        verbose_name = "上传文件"
        verbose_name_plural = verbose_name


class InstagramMedia(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="用户")
    media_id = models.CharField(max_length=200, verbose_name="media_id", default="")
    url = models.URLField(max_length=400, verbose_name="url", default="")
    caption = models.CharField(max_length=500, verbose_name="caption", default="", null=True, blank=True)

    class Meta:
        verbose_name = "InstagramMedia"
        verbose_name_plural = verbose_name