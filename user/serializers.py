from rest_framework import serializers
from user.models import DirFile
from django.contrib.auth.models import User

class DirFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirFile
        fields = ('pk', 'owner', 'parentId', 'name', 'md5code', 'pathLineage', 'dorf', 'modifiedTime', 'encryption_scheme', 'file_type')

class DirFileDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirFile
        fields = ('pk', 'owner', 'parentId', 'name', 'md5code', 'pathLineage', 'fileContent', 'dorf', 'modifiedTime', 'encryption_scheme', 'file_type')

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('pk', 'username')