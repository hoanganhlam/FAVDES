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
from django.db.models import Q, Count


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
        point_id = self.request.GET.get('point')
        if destination_id:
            addresses = Address.objects.filter(points__destination__id=destination_id)
            q_and = q_and & Q(
                address__id__in=addresses.values('id')
            )
        if point_id:
            addresses = Address.objects.filter(points__id=point_id)
            q_and = q_and & Q(
                address__id__in=addresses.values('id')
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
        if target_id is None and target_content_id is None and point_id is None and destination_id is None:
            # Lấy những activty target đến current_user
            if user.is_authenticated:
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
