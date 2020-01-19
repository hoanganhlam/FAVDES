from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.destination import models
from rest_framework.decorators import api_view
from rest_framework.response import Response


# from datetime import datetime


class DestinationViewSet(viewsets.ModelViewSet):
    models = models.Destination
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.DestinationSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'slug'


class AddressViewSet(viewsets.ModelViewSet):
    models = models.Address
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.DAddressSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['formatted_address']
    lookup_field = 'pk'


class SearchAddressViewSet(viewsets.ModelViewSet):
    models = models.SearchAddress
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.SearchAddressSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['address']
    lookup_field = 'pk'
