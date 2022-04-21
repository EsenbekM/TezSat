from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import boto3
from .utils import get_local_files

MEDIA_ROOT = settings.MEDIA_ROOT


class Command(BaseCommand):
    help = 'sync media files with storage'

    def handle(self, *args, **options):
        session = boto3.session.Session()
        client = session.client('s3',
                                region_name=settings.AWS_S3_REGION_NAME,
                                endpoint_url=settings.AWS_S3_ENDPOINT_URL,
                                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY)
        local_files = get_local_files(MEDIA_ROOT)
        local_files_len = len(local_files)
        for i, file in enumerate(local_files):
            print('uploading', i + 1, 'out of', local_files_len, file)
            client.upload_file(file,
                               settings.AWS_STORAGE_BUCKET_NAME,
                               file[len(MEDIA_ROOT):],
                               ExtraArgs={'ACL': 'public-read'})
