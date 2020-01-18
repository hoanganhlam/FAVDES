from apps.activity import models
from rest_framework import serializers
from apps.media.api.serializers import MediaSerializer
from apps.authentication.api.serializers import UserSerializer
from apps.destination.api.serializers import DAddressSerializer, DestinationSerializer, PointSerializer


class TaxonomySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Taxonomy
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }


class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Post
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['medias'] = MediaSerializer(many=True, read_only=True)
        self.fields['taxonomies'] = TaxonomySerializer(many=True, read_only=True)
        self.fields['user'] = UserSerializer(read_only=True)

        return super(PostSerializer, self).to_representation(instance)


class ActivitySerializer(serializers.ModelSerializer):
    is_voted = serializers.SerializerMethodField()
    total_vote = serializers.SerializerMethodField()
    slug = serializers.SerializerMethodField()

    class Meta:
        model = models.Activity
        fields = ['id', 'verb', 'created', 'is_voted', 'total_vote', 'slug', 'address', 'temp']

    def to_representation(self, instance):
        self.fields['address'] = DAddressSerializer(read_only=True)
        return super(ActivitySerializer, self).to_representation(instance)

    def get_is_voted(self, instance):
        user = self.context['request'].user
        return user in instance.voters.all()

    def get_total_vote(self, instance):
        return instance.voters.count()

    def get_slug(self, instance):
        d_str = 'anywhere'
        flag = 'stay'
        if instance.address:
            d = instance.address.destinations.first()
            if d is None:
                p = instance.address.points.first()
                if p:
                    d = p.destination
            if d:
                d_str = d.slug
        return '/' + d_str + '/' + flag + '/' + str(instance.id)


class CommentSerializer(serializers.ModelSerializer):
    is_voted = serializers.SerializerMethodField()

    class Meta:
        model = models.Comment
        fields = '__all__'
        extra_fields = ['is_voted']

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(CommentSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields

    def get_is_voted(self, instance):
        user = self.context['request'].user
        return user in instance.voters.all()

    def to_representation(self, instance):
        self.fields['user'] = UserSerializer(read_only=True)
        return super(CommentSerializer, self).to_representation(instance)


def convert_serializer(instance):
    out = {}
    if instance:
        if instance.__class__.__name__ == "User":
            out = UserSerializer(instance).data
        elif instance.__class__.__name__ == "Destination":
            out = DestinationSerializer(instance).data
        elif instance.__class__.__name__ == "Point":
            out = PointSerializer(instance).data
        elif instance.__class__.__name__ == "Post":
            out = PostSerializer(instance).data
        elif instance.__class__.__name__ == "Comment":
            out = CommentSerializer(instance).data
        elif instance.__class__.__name__ == "Address":
            destination = instance.destinations.first()
            point = instance.points.first()
            if destination:
                out = DestinationSerializer(destination).data
                out["model_name"] = destination.__class__.__name__
            elif point:
                out = PointSerializer(destination).data
                out["model_name"] = point.__class__.__name__
            return out
        if out:
            out["model_name"] = instance.__class__.__name__
            return out
    return None
