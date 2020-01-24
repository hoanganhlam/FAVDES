from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import Profile
from rest_auth.registration.serializers import RegisterSerializer
from apps.media.api.serializers import MediaSerializer
from apps.activity.actions import is_following


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['media', 'description', 'nick']

    def to_representation(self, instance):
        self.fields['media'] = MediaSerializer(read_only=True)
        return super(ProfileSerializer, self).to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile', 'is_following', 'is_staff']

    def get_profile(self, instance):
        if hasattr(instance, 'profile'):
            return ProfileSerializer(instance.profile).data
        return None

    def get_is_following(self, instance):
        if self.context.get("request"):
            user = self.context.get("request").user
            if user.is_authenticated:
                return is_following(user, instance)
        return False


class NameRegistrationSerializer(RegisterSerializer):
    def update(self, instance, validated_data):
        pass

    def create(self, validated_data):
        pass

    first_name = serializers.CharField(required=True)
    last_name = serializers.CharField(required=True)

    def custom_signup(self, request, user):
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save(update_fields=['first_name', 'last_name'])
