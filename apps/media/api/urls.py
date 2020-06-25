from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'medias', views.MediaViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^medias/(?P<pk>[0-9]+)/is-voted/$', views.is_voted),
    url(r'^medias/(?P<pk>[0-9]+)/vote/$', views.vote),
]
