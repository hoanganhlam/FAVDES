from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.activity import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.activity import action
from apps.destination.models import Address
from django.contrib.contenttypes.models import ContentType


# from datetime import datetime


class TaxonomyViewSet(viewsets.ModelViewSet):
    models = models.Taxonomy
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.TaxonomySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title']
    lookup_field = 'slug'


class PostViewSet(viewsets.ModelViewSet):
    models = models.Post
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.PostSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter, SearchFilter]
    search_fields = ['title']
    lookup_field = 'slug'

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        address_id = request.data.get("address")
        tagged = request.data.get("tagged")
        address = Address.objects.get(pk=int(address_id))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        action.send(sender=instance.user, verb='POSTED', action_object=instance, address=address)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ActivityViewSet(viewsets.ModelViewSet):
    models = models.Activity
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.ActivitySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'


class CommentViewSet(viewsets.ModelViewSet):
    models = models.Comment
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.CommentSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        post_id = int(request.GET.get("post"))
        self.queryset = self.queryset.filter(activity__id=post_id)
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@api_view(['POST'])
def vote_post(request, pk):
    user = request.user
    if not request.user.is_authenticated:
        result = False
    else:
        post = models.Activity.objects.get(pk=pk)
        if user in post.voters.all():
            post.voters.remove(user)
            result = False
        else:
            post.voters.add(user)
            result = True
    return Response({
        "result": result
    })


@api_view(['POST'])
def vote_comment(request, pk):
    user = request.user
    if not user.is_authenticated:
        result = False
    else:
        instance = models.Comment.objects.get(pk=pk)
        if user in instance.voters.all():
            instance.voters.remove(user)
            result = False
        else:
            instance.voters.add(user)
            result = True
    return Response({
        "result": result
    })


@api_view(['POST'])
def follow(request):
    content_type_id = request.POST.get("content_type_id")
    object_id = request.POST.get("object_id")
    user = request.user
    if not request.user.is_authenticated:
        return Response(None)
    else:
        instance = models.Follow.objects.filter(user=user, content_type_id=content_type_id, object_id=object_id).first()
        if instance is None:
            instance = models.Follow(user=user, content_type_id=content_type_id, object_id=object_id)
            instance = instance.save()
        return Response(instance.id)


@api_view(['GET'])
def get_config(request):
    return Response(
        {
            "content_type": {
                "point": ContentType.objects.get(model="point").pk,
                "destination": ContentType.objects.get(model="destination").pk,
                "user": ContentType.objects.get(model="user").pk,
                "post": ContentType.objects.get(model="post", app_label="activity").pk,
                "address": ContentType.objects.get(model="address").pk,
                "activity": ContentType.objects.get(model="activity").pk,
            }
        }
    )
