from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.trip.models import Schedule, Task, Discussion


# from datetime import datetime


class ScheduleViewSet(viewsets.ModelViewSet):
    models = Schedule
    queryset = models.objects.order_by('-id').prefetch_related(
        'taxonomies', 'media__user', 'destination_start__medias', 'destination_start__address',
        'destination_end__medias', 'destination_end__address') \
        .select_related('destination_end', 'destination_start', 'media', 'user')
    serializer_class = serializers.ScheduleSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'note']
    lookup_field = 'id'

    def list(self, request, *args, **kwargs):
        return super(ScheduleViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(viewsets.ModelViewSet):
    models = Task
    queryset = models.objects.order_by('-id').select_related('destination', 'user').prefetch_related(
        'destination__medias', 'destination__address')
    serializer_class = serializers.TaskSerializer
    permission_classes = permissions.IsAuthenticatedOrReadOnly,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title']
    lookup_field = 'id'

    def list(self, request, *args, **kwargs):
        return super(TaskViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DiscussionViewSet(viewsets.ModelViewSet):
    models = Discussion
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.DiscussionSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['content']
    lookup_field = 'id'

    def list(self, request, *args, **kwargs):
        return super(DiscussionViewSet, self).list(request, *args, **kwargs)
