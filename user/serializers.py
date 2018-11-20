from rest_framework import serializers
from user.models import DirFile

class DirFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = DirFile
        fields = ('owner', 'parentId', 'name', 'depth', 'pathLineage', 'dorf', 'fileContent', 'modifiedTime')
