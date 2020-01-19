from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.destination import models as d_models
from apps.destination.api.serializers import AddressSerializer
from utils.location_checker import google_map_geo_coding, get_address, get_place_photos, get_places_nearby, \
    google_map_autocomplete, get_place, reverse_geocode_geo_coding
from utils.other import get_client_ip, convert_location, make_address, get_parent
from utils.web_checker import get_web_meta, get_description, get_destinations
from instagram_private_api import Client
from utils.instagram import get_instagram_by_tag, get_instagram_users
from apps.media.models import Media
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen, urlparse
from django.core.files import File
from rest_framework import viewsets, permissions
from rest_framework.filters import OrderingFilter
from base import pagination
from . import serializers
from apps.worker import models


# Create your views here.


class IGPostViewSet(viewsets.ModelViewSet):
    models = models.IGPost
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.IGPostSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'


class IGUserViewSet(viewsets.ModelViewSet):
    models = models.IGUser
    queryset = models.objects.order_by('-id')
    serializer_class = serializers.IGUserSerializer
    permission_classes = permissions.AllowAny,
    pagination_class = pagination.Pagination
    filter_backends = [OrderingFilter]
    lookup_field = 'pk'


@api_view(['GET'])
def fetch_url(request):
    return Response(get_web_meta(request.GET.get("url")))


@api_view(['GET'])
def fetch_places(request):
    data = get_address(request.GET.get("search"))
    return Response(data)


@api_view(['GET'])
def fetch_place_photos(request):
    data = get_place_photos(request.GET)
    return Response(data)


@api_view(['GET'])
def fetch_address(request):
    search = request.GET.get("search")
    addresses = []
    if search:
        search_address = d_models.SearchAddress.objects.filter(search_keyword=search, address__isnull=False).first()
        # Make Address
        if search_address is None:
            results = get_address(search)
            for result in results.get("results"):
                address = get_parent(result)
                addresses.append(address)
        else:
            addresses.append(search_address.address)
            # Handle Search Address
            ip = get_client_ip(request)
            search_address = d_models.SearchAddress.objects.filter(search_keyword=search, tracking_ip=ip).first()
            if search_address is None:
                d_models.SearchAddress.objects.create(
                    address=search_address.address,
                    search_keyword=search,
                    tracking_ip=get_client_ip(request)
                )
            else:
                search_address.count = search_address.count + 1
                search_address.save()
        return Response({
            "results": AddressSerializer(addresses, many=True).data
        })
    return Response({
        "results": []
    })


@api_view(['GET'])
def fetch_address_autocomplete(request):
    search = request.GET.get("search")
    results = google_map_autocomplete(search)
    output = []
    for result in results:
        address = get_parent(result.get("place_id"))
        output.append(address)
    return Response({
        "results": AddressSerializer(output, many=True).data
    })


@api_view(['GET'])
def fetch_description(request):
    search = request.GET.get("search")
    lang = request.GET.get("lang") or "vi"
    limit = request.GET.get("limit") or 5
    if search:
        data = get_description(lang, search, limit)
        return Response(data)
    return Response({})


@api_view(['GET'])
def fetch_places_places_nearby(request):
    data = get_places_nearby(request.GET)
    request.GET._mutable = True
    for item in data.get("results"):
        address = make_address(item)
        convert_location(address)
    while data.get("next_page_token"):
        request.GET["page_token"] = data.get("next_page_token")
        data = get_places_nearby(request.GET)
        for i in data.get("results"):
            address = make_address(i)
            convert_location(address)
    return Response(data)


@api_view(['GET'])
def fetch_instagram(request):
    user_name = 'hoanglamyeah'
    password = 'Hoanganhlam@no1'

    api = Client(user_name, password)
    # results = api.location_search(latitude=21.0277644, longitude=105.8341598)
    # results = api.location_fb_search(query="Ha Noi", rank_token="08276948-21a8-11ea-8c58-acde48001122")
    # return Response(results)
    results = api.feed_tag(tag="hanoi", rank_token="08276948-21a8-11ea-8c58-acde48001122")
    return Response(results)


@api_view(['GET'])
def fetch_destination(request):
    data = get_destinations()
    return Response({})


@api_view(['GET'])
def fetch_instagram_photos(request):
    get_instagram_by_tag(request.GET.get("search"))
    return Response({})


@api_view(['GET'])
def fetch_google_photos(request):
    results = []
    return Response(results)


@api_view(['GET'])
def fetch_instagram_users(request):
    results = get_instagram_users(request.GET.get("search"))
    return Response(results)


@api_view(['GET'])
def reverse_geocode(request):
    lat = request.GET.get("lat")
    lng = request.GET.get("lng")
    results = reverse_geocode_geo_coding({
        "lat": lat,
        "lng": lng
    })
    out = []
    parent = None
    if results:
        for result in reversed(results):
            address, instance = make_address(result)
            if parent is not None:
                if instance.__class__.__name__ == "Destination":
                    instance.parent = parent
                elif instance.__class__.__name__ == "Point":
                    instance.destination = parent
                instance.save()
                parent = instance
            out.append(address)
    return Response(AddressSerializer(reversed(out), many=True).data)


@api_view(['GET'])
def test(request):
    get_parent("ChIJnSO0gLF5zDYRRDXCO6dzo7c")
    return Response({})

# def test(request):
#     url = "https://instagram.fhan1-1.fna.fbcdn.net/v/t51.2885-15/e35/76886189_580077459204860_3869828130800627167_n.jpg?_nc_ht=instagram.fhan1-1.fna.fbcdn.net&_nc_cat=108&_nc_ohc=J_HSTGbR1SEAX-GxNrn&se=7&oh=aa33e569e38ada5c2b43a4d1082c8181&oe=5E8FBDC8&ig_cache_key=MjIwMjk5Mjc0ODg5Mzk0NDM1MA%3D%3D.2"
#     img_temp = NamedTemporaryFile(delete=True)
#     img_temp.write(urlopen(url).read())
#     name = urlparse(url).path.split('/')[-1]
#     print(name)
#     ext = name.split('.')[-1]
#     if ext in ['jpg', 'jpeg', 'png']:
#         img_temp.flush()
#         img = Media(title=name)
#         img.path.save(name, File(img_temp))
#         print(img)
#     return Response([])
