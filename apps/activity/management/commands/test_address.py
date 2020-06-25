from django.core.management.base import BaseCommand
from utils.other import get_addresses

import json


class Command(BaseCommand):
    def handle(self, *args, **options):
        addresses = get_addresses(search="Alps")
        print(addresses)
