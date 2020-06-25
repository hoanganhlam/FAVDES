from django.core.management.base import BaseCommand
from apps.media.models import Media
from django.utils import timezone
from apps.activity import action
from urllib.request import urlopen, urlparse, Request
from django.core.files.temp import NamedTemporaryFile
from apps.media.api.serializers import MediaSerializer
from apps.activity.models import Activity, Post
from django.core.files import File
import requests
from sorl.thumbnail import delete


class Command(BaseCommand):
    def handle(self, *args, **options):
        medias = Media.objects.filter(properties__width=None)
        for media in medias:
            req = requests.get(url=media.source_url, headers={'User-Agent': 'Mozilla/5.0'}, allow_redirects=True)
            name = urlparse(media.source_url).path.split('/')[-1]
            if media.properties is None:
                media.properties = {}
            if req.status_code == 200:
                disposition = req.headers.get("Content-Disposition")
                if disposition:
                    test = disposition.split("=")
                    if len(test) > 1:
                        name = test[1].replace("\"", "")
                temp = NamedTemporaryFile(delete=True)
                temp.write(req.content)
                temp.flush()
                delete(media.path)
                media.path.save(name, File(temp))
                media.save()
                MediaSerializer.get_sizes(media, media)
            else:
                posts = Post.objects.filter(medias=media)
                for post in posts:
                    activities = Activity.objects.filter(
                        action_object_content_type_id=29,
                        action_object_object_id=str(post.id)
                    )
                    for activity in activities:
                        media.properties["status"] = "DELETED"
                        activity.db_status = -1
                        activity.save()
                        print(activity.id)
            media.properties["width"] = media.path.width
            media.properties["height"] = media.path.width
            media.properties["size"] = media.path.size
            media.save()
            print(media.id)
