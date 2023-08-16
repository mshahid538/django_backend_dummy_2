from rest_framework import serializers

from apps.chat.models import OriginalFileModel, ConvertedFileModel


class OriginalFileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = OriginalFileModel
        fields = ['filename', 'path']


class ConvertedFileModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConvertedFileModel
        fields = ['filename', 'path', 'downloadable']
