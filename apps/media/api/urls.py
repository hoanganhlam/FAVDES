from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'medias', views.MediaViewSet)
router.register(r'media-comments', views.MediaCommentViewSet)
router.register(r'media-taxonomies', views.MediaTaxonomyViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
]
