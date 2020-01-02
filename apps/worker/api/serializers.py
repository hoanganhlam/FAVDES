from apps.worker import models
from rest_framework import serializers


class IGPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IGPost
        fields = '__all__'


class IGUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.IGUser
        fields = '__all__'
