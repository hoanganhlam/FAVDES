from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.destination import models


# from datetime import datetime


class MediaViewSet(viewsets.ModelViewSet):
    models = models.Media
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.MediaSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'
