from rest_framework import serializers
from apps.general.models import Taxonomy


class TaxonomySerializer(serializers.ModelSerializer):
    class Meta:
        model = Taxonomy
        fields = '__all__'
        extra_kwargs = {
            'slug': {'read_only': True}
        }
