from django.core.management.base import BaseCommand, CommandError
from product.models import Product, ProductPhoto
from tezsat.utils import compress_image
from django.core.files.storage import default_storage
from product.settings import ProductState


class Command(BaseCommand):
    help = 'make thumbnails of all products'

    def handle(self, *args, **options):
        products = Product.objects.prefetch_related('photos').filter(state=ProductState.ACTIVE).all()
        to_delete = []
        product_len = len(products)
        print('found', product_len, 'products')
        for i, product in enumerate(products):
            print(f'{i} out of {product_len}')
            photos = product.photos.all()
            for j, photo in enumerate(photos):
                if photo.medium_thumbnail and photo.small_thumbnail:
                    continue
                if not default_storage.exists(photo.photo.name):
                    print(f'{i} out of {product_len} {j}', product.id, 'photo does not exists, mark to delete')
                    to_delete.append(photo.id)
                    continue
                if not photo.medium_thumbnail:
                    print(f'{i} out of {product_len} {j}', product.id, 'medium_thumbnail', photo.photo.name)
                    photo.medium_thumbnail = compress_image(photo.photo, is_medium_thumbnail=True)
                if not photo.small_thumbnail:
                    print(f'{i} out of {product_len} {j}', product.id, 'small_thumbnail', photo.photo.name)
                    photo.small_thumbnail = compress_image(photo.photo, is_small_thumbnail=True)
                photo.save()
        print('deleting photos marked as to delete', len(to_delete))
        ProductPhoto.objects.filter(id__in=to_delete).delete()
