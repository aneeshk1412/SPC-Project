from rest_framework import serializers
from user.models import DirFile
from django.contrib.auth.models import User

class DirFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirFile
        fields = ('pk', 'owner', 'parentId', 'name', 'md5code', 'pathLineage', 'dorf', 'modifiedTime')

class DirFileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirFile
        fields = ('pk', 'owner', 'parentId', 'name', 'md5code', 'pathLineage', 'fileContent', 'dorf', 'modifiedTime')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username')