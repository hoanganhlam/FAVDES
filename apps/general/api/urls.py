from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'taxonomies', views.TaxonomyViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^config', views.get_config),
]
