from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.media import models
from rest_framework.response import Response
from rest_framework.decorators import api_view
from sorl.thumbnail import get_thumbnail

# from datetime import datetime


class MediaViewSet(viewsets.ModelViewSet):
    models = models.Media
    queryset = models.objects.order_by('-id').select_related('user').prefetch_related('taxonomies', 'user__profile')
    serializer_class = serializers.MediaSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title', 'description']
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        for item in self.queryset:
            get_thumbnail(item.path, '270x270', crop='center', quality=100)
            get_thumbnail(item.path, '540x540', crop='center', quality=100)
            get_thumbnail(item.path, '540', crop='noop', quality=100)
        return super(MediaViewSet, self).list(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', True)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if not hasattr(serializer.validated_data, "user"):
            serializer.validated_data["user"] = request.user
        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}
        return Response(serializer.data)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@api_view(['GET'])
def is_voted(request, pk):
    if request.user.is_authenticated:
        media = models.Media.objects.get(pk=pk)
        return Response(request.user in media.voters.all())
    return Response(False)


@api_view(['POST'])
def vote(request, pk):
    if request.user.is_authenticated:
        media = models.Media.objects.get(pk=pk)
        if request.user in media.voters.all():
            media.voters.remove(request.user)
        else:
            media.voters.add(request.user)
            return Response(True)
    return Response(False)
