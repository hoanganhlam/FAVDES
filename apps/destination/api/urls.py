from . import views
from rest_framework.routers import DefaultRouter
from django.conf.urls import include, url

router = DefaultRouter()
router.register(r'destinations', views.DestinationViewSet)
router.register(r'addresses', views.AddressViewSet)
router.register(r'search-addresses', views.SearchAddressViewSet)
router.register(r'dars', views.DARViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^ranking/$', views.ranking),
]
