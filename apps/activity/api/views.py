from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter, SearchFilter
from base import pagination
from . import serializers
from apps.activity import models
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from apps.activity import action
from apps.destination.models import Address, Destination
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.contrib.auth.models import User
from apps.authentication.models import Profile
from apps.media.models import Media
from utils.other import get_addresses


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
        address = Address.objects.get(pk=int(address_id))
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        destination_name = request.data.get("destination_name")
        if request.data.get("destination_name"):
            destination = Destination.objects.filter(address=address, title=destination_name).first()
            if destination is None:
                destination = Destination(address=address, title=destination_name, user=request.user)
                check = address.destinations.first()
                if check:
                    destination.parent = check.parent
                destination.save()
        else:
            destination = address.destinations.first()
        action.send(sender=instance.user, verb='POSTED', action_object=instance, address=address, target=destination)
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

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        ordering = self.request.GET.get('ordering')
        if ordering == 'popular':
            queryset = self.models.objects.annotate(vot_count=Count('votes'), comt_count=Count('comments')) \
                .order_by('-vot_count', '-comt_count')
        # Query
        q_or = Q()
        q_and = Q()
        user = self.request.user
        target_id = self.request.GET.get('target')
        target_content_id = self.request.GET.get('target_content')
        destination_id = self.request.GET.get('destination')
        address_id = self.request.GET.get('address')
        if destination_id:
            addresses = Address.objects.filter(destinations__id=destination_id)
            q_and = q_and & Q(
                address__id__in=addresses.values('id')
            )
        if address_id:
            q_and = q_and & Q(
                address__id=address_id
            )
        if target_id and target_content_id:
            q_temp = Q(
                target_content_type__id=int(target_content_id),
                target_object_id=target_id
            ) | Q(
                action_object_content_type=int(target_content_id),
                action_object_object_id=target_id,
            ) | Q(
                actor_content_type=int(target_content_id),
                actor_object_id=target_id
            )
            q_and = q_and & q_temp
        if target_id is None and target_content_id is None and destination_id is None:
            # Lấy những activty target đến current_user
            if user.is_authenticated and not user.is_staff:
                q_or = q_or | Q(
                    target_content_type=ContentType.objects.get_for_model(user),
                    target_object_id=user.pk
                ) | Q(
                    action_object_content_type=ContentType.objects.get_for_model(user),
                    action_object_object_id=user.pk
                ) | Q(
                    actor_content_type=ContentType.objects.get_for_model(user),
                    actor_object_id=user.pk
                )
                # Lấy danh sách follow bởi user
                follows = models.Follow.objects.filter(user=user)
                content_types = ContentType.objects.filter(
                    pk__in=follows.values('content_type_id')
                )

                for content_type in content_types:
                    object_ids = follows.filter(content_type=content_type)
                    q_or = q_or | Q(
                        actor_content_type=content_type,
                        actor_object_id__in=object_ids.values('object_id')
                    ) | Q(
                        target_content_type=content_type,
                        target_object_id__in=object_ids.filter(actor_only=False).values('object_id')
                    ) | Q(
                        action_object_content_type=content_type,
                        action_object_object_id__in=object_ids.filter(actor_only=False).values('object_id')
                    )
        self.queryset = queryset.filter(q_or & q_and, **kwargs)
        for item in self.queryset:
            if item.temp is None:
                item.temp = {
                    "actor": serializers.convert_serializer(item.actor),
                    "action_object": serializers.convert_serializer(item.action_object),
                    "target": serializers.convert_serializer(item.target)
                }
                item.save()
        return super(ActivityViewSet, self).list(request, *args, **kwargs)


class CommentViewSet(viewsets.ModelViewSet):
    models = models.Comment
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.CommentSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'

    def list(self, request, *args, **kwargs):
        activity = int(request.GET.get("activity"))
        self.queryset = self.queryset.filter(activity__id=activity)
        return super(CommentViewSet, self).list(request, *args, **kwargs)

    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)


@api_view(['POST'])
def import_data(request):
    if not request.user.is_authenticated:
        return Response({})
    instance = models.Post.objects.filter(source__pexels=request.data.get("id")).first()
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
            instance = models.Post(user=user, source=source, content=request.data.get("title"))
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
    content_type_id = request.data.get("content_type_id")
    object_id = request.data.get("object_id")
    user = request.user
    if not request.user.is_authenticated:
        return Response(False)
    else:
        instance = models.Follow.objects.filter(user=user, content_type_id=content_type_id, object_id=object_id).first()
        if instance is None:
            instance = models.Follow(user=user, content_type_id=content_type_id, object_id=object_id)
            instance.save()
            return Response(True)
        else:
            instance.delete()
            return Response(False)


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


def make_temp(request):
    items = models.Activity.objects.all()
    for item in items:
        item.temp = {
            "actor": serializers.convert_serializer(item.actor),
            "action_object": serializers.convert_serializer(item.action_object),
            "target": serializers.convert_serializer(item.target)
        }
        item.save()
    return Response(True)


@api_view(['GET'])
def is_following(request):
    if request.user.is_authenticated:
        content_type_id = request.GET.get("content-type-id")
        object_id = request.GET.get("object-id")
        instance = models.Follow.objects.filter(
            user=request.user,
            content_type_id=content_type_id,
            object_id=object_id
        ).first()
        if instance:
            return Response(True)
    return Response(False)
