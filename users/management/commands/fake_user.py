from django.core.management.base import BaseCommand
from location.models import Location
from users.models import User
import random
import faker
from django.contrib.auth.hashers import make_password


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def handle(self, *args, **options):
        count = options['count']
        fake = faker.Faker(['ru_RU'])
        locations = Location.objects.all()
        users = []
        for i in range(count):
            user = User()
            user.name = fake.name()
            user.email = fake.email()
            user.location = random.choice(locations)
            user.password = make_password(user.email)
            users.append(user)
            print(i + 1, user.email)
        User.objects.bulk_create(users)
