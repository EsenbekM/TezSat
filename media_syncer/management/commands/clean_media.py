import os

from django.conf import settings
from django.core.management.base import BaseCommand

from business.models import Business
from category.models import Category
from chat.models import ChatPhoto
from product.models import ProductPhoto
from users.models import User
from .utils import get_local_files

MEDIA_ROOT = settings.MEDIA_ROOT


class Command(BaseCommand):
    help = 'sync media files with storage'

    files_path = []

    def add_arguments(self, parser):
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Delete found files',
        )

    def filter_images(self, model, files, field='photo'):
        to_update = []
        for item in model.objects.all():
            img = getattr(item, field)
            if img.name:
                if img.name in files:
                    files.remove(img.name)
                else:
                    to_update.append(item.id)
            else:
                to_update.append(item.id)
        return to_update

    def handle(self, *args, **options):
        delete = options['delete']
        files = set([file[len(MEDIA_ROOT):] for file in get_local_files(MEDIA_ROOT)])
        print('found local files:', len(files))

        print('fetching user photos...')
        user2update = self.filter_images(User, files)
        print('found', len(user2update), 'objects to update')
        if delete:
            print('updating...')
            User.objects.filter(id__in=user2update).update(photo=None)

        print('fetching product photos...')
        product2update = self.filter_images(ProductPhoto, files)
        print('found', len(product2update), 'objects to delete')
        if delete:
            print('deleting...')
            ProductPhoto.objects.filter(id__in=product2update).delete()

        print('fetching chat photos...')
        chat2update = self.filter_images(ChatPhoto, files)
        print('found', len(chat2update), 'objects to delete')
        if delete:
            print('deleting...')
            ChatPhoto.objects.filter(id__in=chat2update).delete()

        print('fetching category icons...')
        category2update = self.filter_images(Category, files, field='icon')
        print('found', len(category2update), 'objects to update')
        if delete:
            print('updating...')
            Category.objects.filter(id__in=category2update).update(icon=None)

        print('fetching business banners...')
        business2update = self.filter_images(Business, files, field='banner')
        print('found', len(business2update), 'objects to update')
        if delete:
            print('updating...')
            Business.objects.filter(id__in=business2update).update(banner=None)

        print('found', len(files), 'local files to delete')
        if delete:
            print('deleting...')
            for file in files:
                os.remove(os.path.join(MEDIA_ROOT, file))
        print('successfully done')
