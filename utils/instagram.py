from utils.slug import _slug_strip, vi_slug
from instagram_private_api import Client, ClientCompatPatch
from apps.worker.models import IGUser, IGPost
from apps.media.models import Media
from django.core.files.temp import NamedTemporaryFile
from urllib.request import urlopen, urlparse
from django.core.files import File


def get_instagram_by_tag(search, max_id=None):
    user_name = 'lam.laca'
    password = 'Hoanganhlam@no99'
    api = Client(user_name, password)
    keyword = _slug_strip(vi_slug(search), separator="")
    if max_id:
        results = api.feed_tag(keyword, rank_token="08276948-21a8-11ea-8c58-acde48001122", max_id=max_id)
    else:
        results = api.feed_tag(keyword, rank_token="08276948-21a8-11ea-8c58-acde48001122")
    # next_max_id = results.get('next_max_id')
    # while next_max_id:
    #     get_instagram_by_tag(search, max_id=next_max_id)
    return list(map(extract_instagram, results.get("items")))


def get_instagram_users(search, max_id=None):
    user_name = 'lam.laca'
    password = 'Hoanganhlam@no99'
    api = Client(user_name, password)
    if max_id:
        results = api.search_users(search, max_id=max_id)
    else:
        results = api.search_users(search)
    return results


def extract_instagram(item):
    place = item.get("location")
    location = None
    if item.get("lat") is not None and item.get("lng") is not None:
        location = {
            "lat": item.get("lat"),
            "lng": item.get("lng")
        }

    caption = None if item.get("caption") is None else item.get("caption").get("text")
    user_raw = item.get("user")
    images = []
    if item.get("image_versions2") or item.get("image"):
        images = [extract_ig_media(item)]
    if item.get("carousel_media"):
        x = item.get("carousel_media")
        images = list(map(extract_ig_media, x))

    user = {
        "instagram_id": user_raw.get("pk"),
        "full_name": user_raw.get("full_name"),
        "username": user_raw.get("username"),
    }

    ig_user = IGUser.objects.filter(instagram_id=user.get("instagram_id")).first()
    if ig_user is None:
        ig_user = IGUser.objects.create(
            instagram_id=user_raw.get("pk"),
            full_name=user_raw.get("full_name"),
            username=user_raw.get("username"),
        )

    tags = [word.replace('#', '') for word in caption.split() if word.startswith('#')]
    ig_post = IGPost.objects.filter(instagram_id=item.get("pk")).first()
    if ig_post is None:
        ig_post = IGPost.objects.create(
            instagram_id=item.get("pk"),
            tags=tags,
            user=ig_user,
            caption=caption,
            coordinate=location,
        )
        for image_url in images:
            img_temp = NamedTemporaryFile(delete=True)
            img_temp.write(urlopen(image_url).read())
            name = urlparse(image_url).path.split('/')[-1]
            ext = name.split('.')[-1]
            if ext in ['jpg', 'jpeg', 'png']:
                img_temp.flush()
                img = Media(title=name)
                img.path.save(name, File(img_temp))
                ig_post.photos.add(img)
        ig_post.save()

    return {
        "id": item.get("pk"),
        "created": item.get("taken_at"),
        "caption": caption,
        "user": user,
        "images:": images,
        "place": place,
        "location": location
    }


def extract_ig_media(item):
    image = None
    if item.get("image_versions2"):
        image = item.get("image_versions2").get("candidates")[0].get("url")
    if item.get("image"):
        image = item.get("image").get("candidates")[0].get("url")
    return image
