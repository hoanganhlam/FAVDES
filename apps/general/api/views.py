from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.general.models import Taxonomy
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db import connection


class TaxonomyViewSet(viewsets.ModelViewSet):
    models = Taxonomy
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.TaxonomySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title']
    lookup_field = 'slug'


@api_view(['GET'])
def get_config(request):
    return Response(
        {
            "content_type": {
                "destination": ContentType.objects.get(model="destination").pk,
                "user": ContentType.objects.get(model="user").pk,
                "post": ContentType.objects.get(model="post", app_label="activity").pk,
                "address": ContentType.objects.get(model="address").pk,
                "activity": ContentType.objects.get(model="activity").pk,
            }
        }
    )


@api_view(['GET'])
def random_user(request):
    u = User.objects.order_by('?').first()
    with connection.cursor() as cursor:
        cursor.execute("SELECT FETCH_USER(%s)", [u.id])
        out = cursor.fetchone()[0]
    return Response(out)

