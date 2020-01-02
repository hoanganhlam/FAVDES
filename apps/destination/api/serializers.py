from apps.destination import models
from rest_framework import serializers
from apps.media.api.serializers import MediaSerializer
from apps.authentication.api.serializers import UserSerializer


class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Destination
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['photos'] = MediaSerializer(many=True, read_only=True)
        self.fields['address'] = AddressSerializer(read_only=True)
        return super(DestinationSerializer, self).to_representation(instance)


class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Point
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }

    def to_representation(self, instance):
        self.fields['photos'] = MediaSerializer(many=True, read_only=True)
        self.fields['address'] = AddressSerializer(read_only=True)
        return super(PointSerializer, self).to_representation(instance)


class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Address
        fields = '__all__'


class SearchAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SearchAddress
        fields = '__all__'
