import requests
from bs4 import BeautifulSoup
import json
from apps.destination import models as d_models
from utils.slug import vi_slug, _slug_strip
from apps.media.models import Media
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen, urlparse
from django.core.files import File


def get_description(lang, search, limit):
    url = "https://" + lang + ".wikipedia.org/w/api.php?action=opensearch&format=json&formatversion=2&namespace=0&suggest=true"
    r = requests.get(
        url,
        params={"search": search, "limit": limit},
        headers={"Content-Type": "text/html; charset=UTF-8"}
    )
    data = r.json()
    return data


def get_web_meta(url):
    r = requests.get(url)
    soup = BeautifulSoup(r.content, features="html.parser")
    title = ""
    if soup.title:
        title = soup.title.string
    description = soup.find("meta", property="og:description")
    if description is None:
        description = soup.find("meta", property="description")
    if description:
        description = description.get('content')
    else:
        description = ''
    images = []
    for img in soup.findAll('img'):
        images.append(img.get('src'))
    data = {
        "title": title,
        "description": description,
        "images": images
    }
    return data


def get_destinations(deep=0, e_id=36, offset=0, destination=None):
    url = "https://cms.lonelyplanet.com/graphql"
    place_types = ["City", "Neighborhood"]
    limit = 12
    v_e_id = e_id
    v_offset = offset

    variables = {
        "limit": limit,
        "placeType": [place_types[deep]],
        "sort": [
            {
                "field": "field_plc_name",
                "direction": "ASC"
            }
        ],
        "offset": v_offset,
        "entityId": v_e_id
    }
    extensions = {
        "persistedQuery": {
            "version": 1,
            "sha256Hash": "0ea1810f01b3bf8688b460d8c4dd182ce576772cb407619c6e63d0188c255c24"
        }
    }

    print("go")
    response = requests.get(
        url,
        params={
            "operationName": "descendantsQuery",
            "variables": json.dumps(variables).encode(encoding="utf-8"),
            "extensions": json.dumps(extensions).encode(encoding="utf-8")
        }
    )

    data = response.json()
    count = data.get("data").get("nodeQuery").get("count") or 0
    entities = data.get("data").get("nodeQuery").get("entities")
    for place in entities:
        images = []
        if place.get("images") and place.get("images").get("entities"):
            images = place.get("images").get("entities")
        slug = _slug_strip(vi_slug(place.get("fieldPlcName")))

        photos = list(map(extract_lonely_image, images))
        destination = d_models.Destination.objects.filter(slug=slug).first()
        point = d_models.Point.objects.filter(slug=slug).first()
        if destination is None and point is None:
            if deep == 0:
                parent = None
                ancestries = list(reversed(place.get("fieldPlcAncestry")))
                if ancestries:
                    for ancestry in ancestries:
                        entity = ancestry.get("entity")
                        slug2 = _slug_strip(vi_slug(entity.get("fieldPlcName")))
                        new_parent = d_models.Destination.objects.filter(slug=slug2).first()
                        if new_parent is None:
                            new_parent = d_models.Destination.objects.create(
                                title=entity.get("fieldPlcName"),
                                slug=slug2,
                                parent=parent
                            )
                        else:
                            new_parent.parent = parent
                            new_parent.save()
                        parent = new_parent

                if destination is None:
                    destination = d_models.Destination.objects.create(
                        title=place.get("fieldPlcName"),
                        slug=slug,
                        parent=parent,
                    )
                else:
                    destination.parent = parent

                for image_url in photos:
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(urlopen(image_url).read())
                    name = urlparse(image_url).path.split('/')[-1]
                    ext = name.split('.')[-1]
                    if ext in ['jpg', 'jpeg', 'png']:
                        img_temp.flush()
                        img = Media(title=name)
                        img.path.save(name, File(img_temp))
                        destination.photos.add(img)
                destination.save()
                get_destinations(deep=1, e_id=place.get("entityId"), destination=destination)
            if deep == 1:
                d_models.Point.objects.create(
                    title=place.get("fieldPlcName"),
                    slug=slug,
                    destination=destination,
                )

    while v_offset < count:
        v_offset = v_offset + limit
        get_destinations(deep, e_id, v_offset)


def extract_place(place):
    images = []
    if place.get("images") and place.get("images").get("entities"):
        images = place.get("images").get("entities")
    return {
        "id": place.get("entityId"),
        "name": place.get("fieldPlcName"),
        "slug": place.get("fieldPlcSlug"),
        "image": list(map(extract_lonely_image, images))
    }


def extract_lonely_image(img):
    return img.get("fieldFile").get("imgixUrl")


def print_iterator(it):
    for x in it:
        print(x)
