from rest_framework import serializers

from apps.copywriting.models import UserProductDesc, InstagramMedia


class UserProductDescSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProductDesc
        fields = ['product_name', 'product_type', 'description', 'result_link', 'thumb_up', 'thumb_down',
                  'edited_result_link', 'id']


class InstagramMediaSerializer(serializers.ModelSerializer):
    class Meta:
        model = InstagramMedia
        fields = ['add_time', 'media_id', 'url', 'caption']
