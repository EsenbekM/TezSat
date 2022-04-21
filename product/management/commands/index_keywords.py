from django.core.management.base import BaseCommand
from django.conf import settings

from product.models import Keyword


class Command(BaseCommand):
    def handle(self, *args, **options):
        with open(f'{settings.BASE_DIR}/keywords.txt', 'r') as file:
            keywords = Keyword.objects.filter(is_search=False)
            keywords.delete()
            lines = file.readlines()
            for i in lines:
                Keyword.objects.create(keyword=i[:-1])
