from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.destination import models
from apps.activity.models import Activity
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q, Count
import datetime


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

    def list(self, request, *args, **kwargs):
        return super(DestinationViewSet, self).list(request, *args, **kwargs)


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


class DARViewSet(viewsets.ModelViewSet):
    models = models.DAR
    queryset = models.objects.order_by('-count')
    serializer_class = serializers.DARSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        date = request.GET.get("date")
        if date:
            rank_date = datetime.datetime.strptime(date, '%d/%m/%Y')
            self.queryset = self.queryset.filter(time=rank_date)
        return super(DARViewSet, self).list(request, *args, **kwargs)


@api_view(['GET'])
def ranking(request):
    date = request.GET.get("date")
    rank_date = datetime.datetime.strptime(date, '%d/%m/%Y')
    for destination in models.Destination.objects.filter(flags__contains=["SPECIAL"]):
        test = models.DAR.objects.filter(time=rank_date, destination=destination).first()
        if test is None:
            children = destination.get_all_children()
            address_ids = list(map(lambda x: x.address.pk, children))
            q = Q(address__id__in=address_ids, created__day=rank_date.day, created__month=rank_date.month,
                  created__year=rank_date.year)
            count = Activity.objects.filter(q).count()
            test = models.DAR(time=rank_date, destination=destination, count=count)
            test.save()
    return Response({})
