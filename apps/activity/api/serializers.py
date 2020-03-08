from rest_framework import serializers
from apps.activity.models import Post, Activity, Comment
from apps.destination.models import Destination, Address
from apps.media.api.serializers import MediaSerializer
from apps.authentication.api.serializers import UserSerializer
from apps.destination.api.serializers import DAddressSerializer, DestinationSerializer, AddressSerializer
from generic_relations.relations import GenericRelatedField
from django.contrib.auth.models import User


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['id', 'title', 'content', 'user', 'medias']
        extra_kwargs = {
            'slug': {'read_only': True},
            'user': {'read_only': True},
        }

    def to_representation(self, instance):
        self.fields['medias'] = MediaSerializer(many=True, read_only=True)
        return super(PostSerializer, self).to_representation(instance)


class ActivitySerializer(serializers.ModelSerializer):
    actor = GenericRelatedField({
        User: UserSerializer(),
        Post: PostSerializer(),
        Destination: DestinationSerializer(),
        Address: AddressSerializer()
    })
    target = GenericRelatedField({
        User: UserSerializer(),
        Post: PostSerializer(),
        Destination: DestinationSerializer(),
        Address: AddressSerializer()
    })
    action_object = GenericRelatedField({
        User: UserSerializer(),
        Post: PostSerializer(),
        Destination: DestinationSerializer(),
        Address: AddressSerializer()
    })

    class Meta:
        model = Activity
        fields = [
            'id', 'verb',
            'created', 'address',
            'actor', 'actor_content_type',
            'target',
            'action_object', 'action_object_content_type'
        ]

    def to_representation(self, instance):
        self.fields['address'] = DAddressSerializer(read_only=True)
        return super(ActivitySerializer, self).to_representation(instance)


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = '__all__'
        extra_kwargs = {
            'user': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        return super(CommentSerializer, self).to_representation(instance)
