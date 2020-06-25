from django.core.management.base import BaseCommand
from bs4 import BeautifulSoup
import requests
from datetime import timedelta
import uuid
from utils.other import get_addresses
from apps.activity.models import Post
from apps.media.models import Media
from apps.authentication.models import Profile
from django.contrib.auth.models import User

import json

arr = [
    # {
    #     "name": "bali",
    #     "title": "Bali, Indonesia"
    # },
    # {
    #     "name": "berlin",
    #     "title": "Berlin, Germany"
    # },
    # {
    #     "name": "bora%20bora",
    #     "title": "Bora Bora"
    # },
    # {
    #     "name": "Budapest",
    #     "title": "Budapest, Hungary"
    # },
    # {
    #     "name": "cambodia",
    #     "title": "Cambodia"
    # },
    # {
    #     "name": "Hanoi",
    #     "title": "Hanoi"
    # },
    # {
    #     "name": "iceland",
    #     "title": "Iceland"
    # },
    # {
    #     "name": "india",
    #     "title": "India"
    # },
    # {
    #     "name": "japan",
    #     "title": "Japan"
    # },
    # {
    #     "name": "korea",
    #     "title": "Korea"
    # },
    # {
    #     "name": "krabi",
    #     "title": "Krabi"
    # },
    # {
    #     "name": "london",
    #     "title": "London"
    # },
    # {
    #     "name": "machu%20picchu",
    #     "title": "Machu Picchu, Peru"
    # },
    # {
    #     "name": "maldives",
    #     "title": "Maldives, Malé"
    # },
    # {
    #     "name": "manhattan",
    #     "title": "Manhattan, New York"
    # },
    # {
    #     "name": "new%20york",
    #     "title": "New York"
    # },
    # {
    #     "name": "norway",
    #     "title": "Norway"
    # },
    # {
    #     "name": "paris",
    #     "title": "Paris"
    # },
    # {
    #     "name": "prague",
    #     "title": "Prague, Czech"
    # },
    # {
    #     "name": "rome",
    #     "title": "Rome, Italy"
    # },
    # {
    #     "name": "saigon",
    #     "title": "Ho Chi Minh City"
    # },
    # {
    #     "name": "sweden",
    #     "title": "Sweden"
    # },
    # {
    #     "name": "switzerland",
    #     "title": "Switzerland"
    # },
    # {
    #     "name": "tokyo",
    #     "title": "Tokyo"
    # },
    # {
    #     "name": "venice",
    #     "title": "Venice"
    # }
]


class Command(BaseCommand):
    def handle(self, *args, **options):
        for a in arr:
            filename = 'data/' + a["name"] + '.json'
            print(filename)
            with open(filename) as json_file:
                data = json.load(json_file)
                i = 0
                for photo in data:
                    i = i + 1
                    instance = Post.objects.filter(source__pexels=photo.get("id")).first()
                    if instance is None and photo.get("download") is not None:
                        url = "https://www.pexels.com/" + photo.get("download")
                        media = Media.objects.filter(source_url=url).first()
                        location = photo.get("location")
                        if location is None or location == "":
                            location = a["title"]
                        if media is None:
                            media = Media.objects.save_url(url=url)
                        if media:
                            username = photo.get("user_username").replace('/@', '')
                            fullname = photo.get("user_full_name")
                            user = User.objects.filter(username=username).first()
                            address = None
                            if location is not None:
                                addresses = get_addresses(search=location)
                                if len(addresses) > 0:
                                    address = addresses[0]
                            if user is None:
                                user = User.objects.create_user(username=username, password="DKM@VKL1234$#@!")
                                Profile.objects.create(user=user, nick=fullname)
                            source = {"pexels": photo.get("id")}
                            print(address)
                            instance = Post(
                                user=user,
                                source=source,
                                content=photo.get("title"),
                                address=address,
                                destination=address.destinations.first() if address is not None else None,
                                publish_status="PENDING"
                            )
                            instance.save()
                            instance.medias.add(media)
                            print(instance.id)
