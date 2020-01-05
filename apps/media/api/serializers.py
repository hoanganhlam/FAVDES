from apps.media import models
from rest_framework import serializers
from sorl.thumbnail import get_thumbnail

sizes = ['200_200', '600_200']


class MediaSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()

    class Meta:
        model = models.Media
        fields = '__all__'
        extra_fields = ['sizes']

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(MediaSerializer, self).get_field_names(declared_fields, info)

        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields

    def get_sizes(self, instance):
        if instance.path:
            return {
                "200_200": get_thumbnail(instance.path, '200x200', crop='center', quality=100).url,
                "600_200": get_thumbnail(instance.path, '600x200', crop='center', quality=100).url,
                "530_530": get_thumbnail(instance.path, '530x530', crop='center', quality=100).url
            }
        else:
            return {}
