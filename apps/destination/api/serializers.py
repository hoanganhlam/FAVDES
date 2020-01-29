from apps.destination import models
from rest_framework import serializers
from apps.media.api.serializers import MediaSerializer


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Destination
        fields = ['id', 'title', 'slug', 'description', 'user', 'address', 'photos', 'contact']
        extra_kwargs = {
            'slug': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['photos'] = MediaSerializer(many=True, read_only=True)
        self.fields['address'] = AddressSerializer(read_only=True)
        return super(DestinationSerializer, self).to_representation(instance)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'


class SearchAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SearchAddress
        fields = '__all__'


class DAddressSerializer(serializers.ModelSerializer):
    destinations = serializers.SerializerMethodField()

    class Meta:
        model = models.Address
        fields = '__all__'
        extra_fields = ['destinations']

    def get_destinations(self, instance):
        return DestinationSerializer(instance.destinations.all(), many=True).data

    def get_field_names(self, declared_fields, info):
        expanded_fields = super(DAddressSerializer, self).get_field_names(declared_fields, info)
        if getattr(self.Meta, 'extra_fields', None):
            return expanded_fields + self.Meta.extra_fields
        else:
            return expanded_fields


class DARSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DAR
        fields = '__all__'

    def to_representation(self, instance):
        self.fields['destination'] = DestinationSerializer(read_only=True)
        return super(DARSerializer, self).to_representation(instance)
