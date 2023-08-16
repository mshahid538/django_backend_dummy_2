from rest_framework import serializers

from apps.users.models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['username', 'password', 'nick_name', 'birthday', 'gender',
                  'address', 'mobile', 'image', 'trial_count', 'total_copy_count',
                  'total_thumb_up_count', 'total_thumb_down_count', 'email', 'first_name', 'last_name']
