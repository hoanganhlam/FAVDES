from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'activities', views.ActivityViewSet)
router.register(r'comments', views.CommentViewSet)
router.register(r'posts', views.PostViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^is-following', views.is_following),
    url(r'^activities/(?P<pk>[0-9]+)/vote$', views.vote_post),
    url(r'^comments/(?P<pk>[0-9]+)/vote$', views.vote_comment),
    url(r'^follow', views.follow),
    url(r'^check-vote', views.get_vote_object),
]
