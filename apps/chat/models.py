from django.contrib.auth import get_user_model
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.users.models import BaseModel

UserProfile = get_user_model()


class UserInputText(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="用户")
    
    user_input_text = models.CharField(max_length=1000, verbose_name="用户输入文字")

    class Meta:
        verbose_name = "用户输入文字"
        verbose_name_plural = verbose_name


class OriginalFileModel(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="用户")
    
    filename = models.CharField(max_length=1000, verbose_name="filename")
    path = models.CharField(max_length=1000, verbose_name="path")


    class Meta:
        verbose_name = "Original File"
        verbose_name_plural = "Original Files"

class ConvertedFileModel(BaseModel):
    user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        verbose_name="用户")
    
    filename = models.CharField(max_length=1000, verbose_name="filename")
    path = models.CharField(max_length=1000, verbose_name="path")
    downloadable = models.BooleanField(default=True)


    class Meta:
        verbose_name = "Converted File"
        verbose_name_plural = "Converted Files"