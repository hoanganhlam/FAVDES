from utils.location_types import destinations, points
from apps.destination import models as d_models
from utils.slug import vi_slug, _slug_strip
from utils.google_images_download import google_images_download


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def check_inner(array, array2):
    for i in array:
        if i in array2:
            return True
    return False


def convert_location(name, address):
    title = _slug_strip(vi_slug(name), " ")
    slug = _slug_strip(vi_slug(title))
    if check_inner(address.types, destinations):
        destination = d_models.Destination.objects.filter(slug=slug).first()
        if destination is None:
            d_models.Destination.objects.create(
                address=address,
                title=name
            )
        else:
            destination.address = address
            destination.save()
    if check_inner(address.types, points):
        point = d_models.Point.objects.filter(slug=slug).first()
        if point is None:
            d_models.Point.objects.create(
                address=address,
                title=name
            )
        else:
            point.address = address
            point.save()


def make_address(g_location):
    address = d_models.Address.objects.filter(place_id=g_location.get("place_id")).first()
    if address is None:
        address = d_models.Address.objects.create(
            formatted_address=g_location.get("formatted_address") or g_location.get("vicinity"),
            geometry=g_location.get("geometry"),
            place_id=g_location.get("place_id"),
            types=g_location.get("types"),
            address_components=g_location.get("address_components"),
        )
    else:
        address.address_components = g_location.get("address_components")
        address.formatted_address = g_location.get("formatted_address") or g_location.get("vicinity")
        address.geometry = g_location.get("geometry")
        address.save()
    return address
