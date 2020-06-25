from rest_framework.decorators import api_view
from rest_framework.response import Response
from apps.destination import models as d_models
from apps.destination.api.serializers import AddressSerializer
from utils.location_checker import get_address, get_place_photos, get_places_nearby, reverse_geocode_geo_coding
from utils.other import convert_location, make_address, get_parent
from utils.web_checker import get_web_meta, get_description
from utils.instagram import get_instagram_by_tag, get_instagram_users
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
        search_address = d_models.SearchAddress.objects.filter(search_keyword=search).first()
        # Make Address
        if search_address is None:
            results = get_address(search)
            search_address = d_models.SearchAddress(search_keyword=search)
            search_address.save()
            for result in results.get("results"):
                address = get_parent(result)
                search_address.addresses.add(address)
                addresses.append(address)
            search_address.save()
        else:
            addresses = search_address.addresses.all()
            search_address.count = search_address.count + 1
            search_address.save()
        return Response({
            "results": AddressSerializer(addresses, many=True).data
        })
    return Response({
        "results": []
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
