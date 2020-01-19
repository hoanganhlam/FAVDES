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
    url(r'fetch-place_photos', views.fetch_place_photos),
    url(r'fetch-address-autocomplete', views.fetch_address_autocomplete),
    url(r'fetch-address', views.fetch_address),
    url(r'fetch-description', views.fetch_description),
    url(r'fetch-placcaies-near', views.fetch_places_places_nearby),
    url(r'fetch-places', views.fetch_places),
    url(r'fetch-i-photos', views.fetch_instagram_photos),
    url(r'fetch-g-photos', views.fetch_google_photos),
    url(r'fetch-instagram-users', views.fetch_instagram_users),
    url(r'fetch-instagram', views.fetch_instagram),
    url(r'fetch-destinations', views.fetch_destination),
    # url(r'^point/(?P<label>\w+)/$', views.index_point),
]
