from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.activity.models import Activity, Post, Comment, Follow
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.activity import action
from apps.destination.models import Destination
from django.contrib.auth.models import User
from apps.authentication.models import Profile
from apps.media.models import Media
from utils.other import get_addresses
from django.db import connection
from utils.other import get_paginator


class PostViewSet(viewsets.ModelViewSet):
    models = Post
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
        destination_id = request.data.get("destination")
        destination = Destination.objects.get(pk=int(destination_id))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        action.send(sender=instance.user, verb='POSTED', action_object=instance, destination=destination)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class ActivityViewSet(viewsets.ModelViewSet):
    models = Activity
    queryset = models.objects.order_by('-id') \
        .select_related('address') \
        .prefetch_related('address__destinations', 'actor', 'action_object', 'target')
    serializer_class = serializers.ActivitySerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        target_id = self.request.GET.get('target')
        target_content_id = self.request.GET.get('target_content')
        destination_id = self.request.GET.get('destination')
        address_id = self.request.GET.get('address')
        hash_tag = self.request.GET.get('hash_tag')
        p = get_paginator(request)
        auth_id = self.request.user.id if self.request.user.is_authenticated else None
        with connection.cursor() as cursor:
            cursor.execute("SELECT FETCH_ACTIVITIES(%s, %s, %s, %s, %s, %s, %s, %s)",
                           [
                               p.get("page_size"),
                               p.get("offs3t"),
                               target_content_id,
                               target_id,
                               auth_id,
                               destination_id,
                               address_id,
                               '{' + hash_tag + '}' if hash_tag else None
                           ])
            return Response(cursor.fetchone()[0])

    def retrieve(self, request, *args, **kwargs):
        user_id = self.request.user.id if self.request.user.is_authenticated else None
        with connection.cursor() as cursor:
            cursor.execute("SELECT FETCH_ACTION(%s, %s)", [kwargs.get("pk"), user_id])
            out = cursor.fetchone()[0]
        return Response(out)


class CommentViewSet(viewsets.ModelViewSet):
    models = Comment
    queryset = models.objects.order_by('-id') \
        .select_related('user') \
        .select_related('user__profile') \
        .select_related('user__profile__media')
    serializer_class = serializers.CommentSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        activity = request.GET.get("activity")
        if activity:
            self.queryset = self.queryset.filter(activity__id=int(activity))
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@api_view(['POST'])
def import_data(request):
    if not request.user.is_authenticated:
        return Response({})
    instance = Post.objects.filter(source__pexels=request.data.get("id")).first()
    if instance is None:
        media = Media.objects.save_url(url=request.data.get("download"))
        if media:
            username = request.data.get("user_username")
            fullname = request.data.get("user_full_name")
            user = User.objects.filter(username=username).first()
            if user is None:
                user = User.objects.create_user(username=username, password="DKM@VKL1234$#@!")
                Profile.objects.create(user=user, nick=fullname)
            source = {"pexels": request.data.get("id")}
            instance = Post(user=user, source=source, content=request.data.get("title"))
            instance.save()
            instance.medias.add(media)
            address = None
            if request.data.get("location"):
                addresses = get_addresses(search=request.data.get("location"))
                if len(addresses) > 0:
                    address = addresses[0]
            action.send(sender=instance.user, verb='POSTED', action_object=instance, address=address)
    return Response({})


@api_view(['POST'])
def vote_post(request, pk):
    user = request.user
    if not request.user.is_authenticated:
        result = False
    else:
        post = Activity.objects.get(pk=pk)
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
        instance = Comment.objects.get(pk=pk)
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
    content_type_id = request.data.get("content_type_id")
    object_id = request.data.get("object_id")
    user = request.user
    if not request.user.is_authenticated:
        return Response(False)
    else:
        instance = Follow.objects.filter(user=user, content_type_id=content_type_id, object_id=object_id).first()
        if instance is None:
            instance = Follow(user=user, content_type_id=content_type_id, object_id=object_id)
            instance.save()
            return Response(True)
        else:
            instance.delete()
            return Response(False)


@api_view(['GET'])
def is_following(request):
    if request.user.is_authenticated:
        content_type_id = request.GET.get("contentType")
        object_id = request.GET.get("objectId")
        instance = Follow.objects.filter(
            user=request.user,
            content_type_id=content_type_id,
            object_id=object_id
        ).first()
        if instance:
            return Response(True)
    return Response(False)


@api_view(['GET'])
def get_vote_object(request):
    pk = request.GET.get("pk")
    activity = Activity.objects.get(pk=pk)
    total_votes = activity.voters.count()
    if request.user.is_authenticated:
        if request.user in activity.voters.all():
            return Response({
                "total": total_votes,
                "is_voted": True
            })
    return Response({
        "total": total_votes,
        "is_voted": False
    })
