import sys
from io import BytesIO
from itertools import chain
from typing import Iterable
from uuid import uuid4

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile

SMALL_THUMBNAIL_SIZE = settings.SMALL_THUMBNAIL_SIZE
MEDIUM_THUMBNAIL_SIZE = settings.MEDIUM_THUMBNAIL_SIZE
WATERMARK_IMAGE = settings.WATERMARK_IMAGE
WATERMARK_PROPORTION_PERCENT = settings.WATERMARK_PROPORTION_PERCENT
WATERMARK_PADDING_PERCENT = settings.WATERMARK_PADDING_PERCENT


def get_filename(old_name):
    format = old_name.rsplit('.', 1)[-1]
    return f'{uuid4()}.{format}'


def put_watermark(image):
    with Image.open(WATERMARK_IMAGE) as watermark:
        original_width, original_height = image.size
        watermark_width, watermark_height = watermark.size
        max_watermark_w = int(original_width * WATERMARK_PROPORTION_PERCENT / 100)
        max_watermark_h = int(original_height * WATERMARK_PROPORTION_PERCENT / 100)
        ratio = min(max_watermark_w/watermark_width, max_watermark_h/watermark_height)
        watermark_width, watermark_height = int(watermark_width * ratio), int(watermark_height * ratio)

        padding_width = int(original_width * WATERMARK_PADDING_PERCENT / 100)
        padding_height = int(original_height * WATERMARK_PADDING_PERCENT / 100)
        # pos_w = int((original_width - watermark_width) - padding_width)
        pos_h = int((original_height - watermark_height) - padding_height)
        pos_w = padding_width
        pos = pos_w, pos_h
        resized_watermark = watermark.resize((watermark_width, watermark_height))
        image.paste(resized_watermark, pos, resized_watermark)


def compress_image(uploaded_image, is_small_thumbnail=False, is_medium_thumbnail=False, quality=50, business=False):
    with Image.open(uploaded_image) as tmp_image:
        if not business:
            put_watermark(tmp_image)
        tmp_image = tmp_image.convert('RGB')
        output_io_stream = BytesIO()
        if is_medium_thumbnail:
            tmp_image.thumbnail(MEDIUM_THUMBNAIL_SIZE)
        if is_small_thumbnail:
            tmp_image.thumbnail(SMALL_THUMBNAIL_SIZE)
        tmp_image.save(output_io_stream, format='JPEG', quality=quality)
        output_io_stream.seek(0)
        uploaded_image = InMemoryUploadedFile(output_io_stream, 'ImageField', f"{uuid4()}.jpg",
                                              'image/jpeg', sys.getsizeof(output_io_stream), None)
        return uploaded_image


def get_children_id(model, ids):
    in_values = ''
    for id in ids:
        in_values += str(id) if not in_values else f', {id}'
    children = model.objects.raw(
        f'''
        with recursive objects as (
            select id from {model._meta.db_table} where id in ({in_values})
            union all
            select c.id from {model._meta.db_table} as c
            join objects on c.parent_id = objects.id
        )
        select id from objects
        '''
    )
    return children


def get_children_id_wo_parent(model, ids):
    in_values = ''
    for id in ids:
        in_values += str(id) if not in_values else f', {id}'
    children = model.objects.raw(
        f'''
        with recursive objects as (
            select id from {model._meta.db_table} where id in ({in_values})
            union all
            select c.id from {model._meta.db_table} as c 
            join objects on c.parent_id = objects.id
        )
        select id from objects where id not in ({in_values})
        '''
    )
    return children

def get_recursive_title(model, id, lang):
    objects = model.objects.raw(
        f'''
        with recursive objects as (
            select *, 1 as level from {model._meta.db_table} where id = {id}
            union all
            select c.*, objects.level + 1 as level
            from {model._meta.db_table} as c
            join objects on c.id = objects.parent_id
        )
        select * from objects order by level
        '''
    )
    title = ''
    for obj in objects:
        if lang == 'ru':
            key = obj.title_ru
        elif lang == 'ky':
            key = obj.title_ky
        else:
            raise KeyError('unknown lang ' + lang)

        title += f'{key} - '
    return title


def get_parent_ids(instance) -> Iterable[int]:
    if instance.parent:
        return chain([instance.parent.id], get_parent_ids(instance.parent))
    return chain()


def get_parent_(instance, result_list):
    if instance:
        result_list.append({
            'id': instance.id,
            'title_ru': instance.title_ru,
            'title_ky': instance.title_ky,
            'title_slug': instance.title_slug
        })
        return chain(
                    get_parent_(instance.parent if instance.parent else None, result_list)
                     )
    return result_list