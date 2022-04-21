import factory


class CategoryFactory(factory.django.DjangoModelFactory):
    """Category Factory"""

    class Meta:
        model = 'category.Category'
