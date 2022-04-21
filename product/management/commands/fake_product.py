from django.core.management.base import BaseCommand, CommandError
from product.models import Product
from product.settings import ProductState, CurrencyType
from category.models import Category
from location.models import Location
from users.models import User
import random
import faker


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('count', type=int)

    def get_leaf(self, model):
        data = []
        for obj in model.objects.all():
            if obj.children.count() == 0:
                data.append(obj)
        return data

    def handle(self, *args, **options):
        count = options['count']
        users = User.objects.all()
        locations = self.get_leaf(Location)
        categories = self.get_leaf(Category)
        fake = faker.Faker(['ru_RU'])
        products = []
        for i in range(count):
            product = Product()
            product.user = random.choice(users)
            product.location = random.choice(locations)
            product.category = random.choice(categories)
            product.currency = CurrencyType.KGS
            product.initial_price = random.randint(1, 10000)
            product.state = ProductState.ACTIVE
            product.price_kgs = product.initial_price
            product.price_usd = product.initial_price

            text = fake.text()
            product.title = text[:50]
            product.description = text
            products.append(product)

            print(i+1, product.title)

        Product.objects.bulk_create(products)
