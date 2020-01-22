from apps.destination import models as d_models
from utils.location_checker import google_map_geo_coding, get_place, get_address


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
    if type(ids) == dict:
        place = ids
    else:
        worker = get_place(ids)
        place = worker.get("result")
    current_address, c_result = make_address(place)
    parent = None
    formatted_address = place.get("formatted_address")
    formatted_address_arr = formatted_address.split(", ")
    length = len(formatted_address_arr)
    for i in range(length):
        address_text_search = ', '.join(map(str, formatted_address_arr[length - i:length]))
        if address_text_search:
            results = get_address(address_text_search).get("results")
            if results and len(results) > 0:
                address, result = make_address(results[0])
                if parent and result.id != parent.id:
                    result.parent = parent
                    result.save()
                if result:
                    parent = result
    if parent and c_result:
        if c_result.parent is None or (c_result.parent and c_result.parent.id != parent.id):
            c_result.parent = parent
            c_result.save()
    return current_address


def get_addresses(search):
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
    return addresses
