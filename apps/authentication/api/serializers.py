from rest_framework import serializers
from django.contrib.auth.models import User
from apps.authentication.models import Profile
from rest_auth.registration.serializers import RegisterSerializer
from apps.media.api.serializers import MediaSerializer
from apps.activity.models import Follow, Activity
from django.contrib.contenttypes.models import ContentType


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ['media', 'description', 'nick']

    def to_representation(self, instance):
        self.fields['media'] = MediaSerializer(read_only=True)
        return super(ProfileSerializer, self).to_representation(instance)


class UserSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile', 'is_staff']

    def get_profile(self, instance):
        if hasattr(instance, 'profile'):
            return ProfileSerializer(instance.profile).data
        return None


class UserDetailSerializer(serializers.ModelSerializer):
    profile = serializers.SerializerMethodField()
    statistic = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'username', 'profile', 'is_staff', 'statistic']

    def get_profile(self, instance):
        if hasattr(instance, 'profile'):
            return ProfileSerializer(instance.profile).data
        return None

    def get_statistic(self, instance):
        content_type = ContentType.objects.get_for_model(instance)
        return {
            "activity": Activity.objects.filter(
                actor_content_type=content_type,
                actor_object_id=instance.pk
            ).count(),
            "following": Follow.objects.filter(user=instance).count(),
            "follower": Follow.objects.filter(
                content_type=content_type,
                object_id=instance.pk
            ).count()
        }


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
