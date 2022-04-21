from django.core.management.base import BaseCommand, CommandError

from django_q.models import Schedule
from product.models import Rate, CurrencyType


class Command(BaseCommand):
    help = 'Init schedule tasks'

    def handle(self, *args, **options):
        Rate.objects.get_or_create(currency=CurrencyType.USD)
        Schedule.objects.get_or_create(
            name='update_currency_rate',
            func='product.jobs.update_currency_rate',
            schedule_type=Schedule.HOURLY,
        )
        Schedule.objects.get_or_create(
            name='update_product_prices',
            func='product.jobs.update_prices',
            schedule_type=Schedule.DAILY
        )
        Schedule.objects.get_or_create(
            name='auto_upvote',
            func='business.jobs.auto_upvote',
            schedule_type=Schedule.MINUTES,
            minutes=5
        )
        Schedule.objects.get_or_create(
            name='regular_upvote',
            func='product.jobs.regular_product_upvote',
            schedule_type=Schedule.MINUTES,
            minutes=3
        )
