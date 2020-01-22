from . import views
from django.conf.urls import include, url
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
# router.register(r'ig-users', views.IGUserViewSet)
# router.register(r'ig-posts', views.IGPostViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'test', views.test),
    url(r'fetch-url', views.fetch_url),
    url(r'fetch-place-reverse', views.reverse_geocode),
    url(r'fetch-place-photos', views.fetch_place_photos),
    url(r'fetch-address', views.fetch_address),
    url(r'fetch-description', views.fetch_description),
    url(r'fetch-places-near', views.fetch_places_places_nearby),
    url(r'fetch-places', views.fetch_places),
    url(r'fetch-i-photos', views.fetch_instagram_photos),
    url(r'fetch-g-photos', views.fetch_google_photos),
]
