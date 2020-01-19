from apps.destination import models as d_models
from utils.location_checker import google_map_geo_coding, get_place


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


def convert_location(address):
    formatted_address_arr = address.formatted_address.split(",")
    name = address.formatted_address
    if len(formatted_address_arr) > 0:
        name = formatted_address_arr[0]
    destination = d_models.Destination.objects.filter(address__formatted_address=address.formatted_address).first()
    if destination is None:
        destination = d_models.Destination(address=address, title=name)
    else:
        destination.address = address
    destination.save()
    return destination


def make_address(g_location):
    address = d_models.Address.objects.filter(place_id=g_location.get("place_id")).first()
    if address is None:
        address = d_models.Address(
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
    destination = convert_location(address)
    return address, destination


def get_parent(ids):
    worker = get_place(ids)
    place = worker.get("result")
    current_address, c_result = make_address(place)
    parent = None
    address = None
    formatted_address = place.get("formatted_address")
    formatted_address_arr = formatted_address.split(", ")
    length = len(formatted_address_arr)

    for i in range(length):
        address_text_search = ', '.join(map(str, formatted_address_arr[length - i:length]))
        results = google_map_geo_coding(address_text_search)
        if results is not None and len(results) > 0:
            address, result = make_address(results[0])
            if parent is not None and result.id != parent.id and parent.__class__.__name__ == "Destination":
                if result.__class__.__name__ == "Destination":
                    result.parent = parent
                    result.save()
            if result is not None:
                parent = result
    if parent is not None and c_result is not None and parent.__class__.__name__ == "Destination":
        if parent.id == c_result.id:
            return address
        if c_result.__class__.__name__ == "Destination":
            c_result.parent = parent
        c_result.save()
    return address
