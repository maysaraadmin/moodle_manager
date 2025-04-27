from rest_framework import serializers
from .models import MoodlePlatform, MoodleUser, UserPlatformAssociation

class MoodlePlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodlePlatform
        fields = ['id', 'name', 'url', 'active', 'created_at']
        read_only_fields = ['id', 'created_at']

class MoodleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MoodleUser
        fields = ['id', 'user', 'moodle_username', 'moodle_userid']
        read_only_fields = ['id']

class UserPlatformAssociationSerializer(serializers.ModelSerializer):
    platform = MoodlePlatformSerializer(read_only=True)
    
    class Meta:
        model = UserPlatformAssociation
        fields = ['id', 'user', 'platform', 'platform_userid', 'platform_username', 'last_sync']
        read_only_fields = ['id', 'last_sync']