from django_elasticsearch_dsl import Document, fields
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, SearchAsYouType, token_filter

from location.models import Location
from location.serializers import ChildLocationSerializer
from product.models import Product, ProductPhoto, ProductContact, ProductParameter
from product.serializers import ProductContactSerializer, ProductParameterSerializer
from tezsat.utils import get_parent_ids
from users.models import User
from users.serializers import PublicUserSerializer

keyword_grammer = analyzer(
    'keyword_grammer',
    tokenizer='standard',
    filter=[
        'lowercase',
        token_filter('1_10_gram', 'edge_ngram', min_gram=1, max_gram=10),
        token_filter('russian_stop', 'stop', stopwords='_russian_'),
    ],
)

text_analyzer = analyzer(
    'text_analyzer',
    tokenizer="standard",
    filter=[
        "lowercase",
        token_filter('1_10_gram', 'edge_ngram', min_gram=1, max_gram=10),
        token_filter('russian_stop', 'stop', stopwords='_russian_'),
        token_filter('russian_marker', 'keyword_marker', keywords=[]),
        token_filter('russian_stemmer', 'stemmer', language='russian'),
    ],
    char_filter=["html_strip"]
)


class SearchAsYouTypeField(fields.DEDField, SearchAsYouType):
    pass


# @registry.register_document
class ProductDocument(Document):
    """
    Managing elasticsearch document
    """
    id = fields.KeywordField()
    category = fields.ObjectField(properties={
        "id": fields.KeywordField(),
        "title_ru": fields.KeywordField(),
        "title_ky": fields.KeywordField(),
    })
    state = fields.KeywordField()
    title = fields.TextField()
    user = fields.ObjectField(properties={
        "id": fields.KeywordField(),
        "name": fields.TextField(required=False, index=False),
        "email": fields.TextField(),
        "phone": fields.TextField(required=False, index=False),
        "date_joined": fields.TextField(),
        "last_active": fields.TextField(),
        "photo": fields.TextField(required=False, index=False),
        "language": fields.KeywordField(),
        "business": fields.KeywordField(required=False),
        "is_business": fields.BooleanField(required=False)
    })
    location = fields.ObjectField(properties={
        "id": fields.KeywordField(),
        "title_ru": fields.KeywordField(),
        "title_ky": fields.KeywordField(),
        "type": fields.KeywordField(),
        "request_ru": fields.TextField(index=False),
        "request_ky": fields.TextField(index=False),
        "parent": fields.KeywordField(required=False),
        "lat": fields.KeywordField(),
        "lng": fields.KeywordField(),
        "is_end": fields.BooleanField(required=False),
        "type_ru": fields.KeywordField(),
        "type_ky": fields.KeywordField()
    })
    photos = fields.ListField(field=fields.ObjectField(required=False, properties={
        "id": fields.KeywordField(),
        "photo": fields.TextField(index=False),
        "medium_thumbnail": fields.TextField(index=False),
        "small_thumbnail": fields.TextField(index=False)
    }))
    contacts = fields.ListField(field=fields.ObjectField(properties={
        "id": fields.KeywordField(),
        "phone": fields.TextField(index=False),
    }))
    parameters = fields.ListField(field=fields.ObjectField(properties={
        'id': fields.KeywordField(),
        'parameter': fields.ObjectField(properties={
            'type': fields.KeywordField(),
            'title_ru': fields.KeywordField(),
            'title_ky': fields.KeywordField(),
            'optional': fields.BooleanField(),
        }),
        'response': fields.KeywordField(),
    }))
    upvote_date = fields.DateField()
    creation_date = fields.DateField()
    like_count = fields.IntegerField()
    favorite_count = fields.IntegerField()
    show_count = fields.IntegerField()
    view_count = fields.IntegerField()

    category_path = fields.ListField(field=fields.KeywordField())
    location_path = fields.ListField(field=fields.KeywordField())

    class Index:
        name = 'product'
        settings = {'number_of_shards': 3,
                    'number_of_replicas': 1}

    class Django:
        model = Product
        fields = [
            'description',
            'currency',
            'initial_price',
            'price_kgs',
            'price_usd',
            'rating',
            'rating_disabled',
        ]

        related_models = [
            User,
            Location,
            ProductPhoto,
            ProductContact,
            ProductParameter,
        ]

    def prepare_category_path(self, instance):
        path_ids = list(get_parent_ids(instance.category))
        path_ids.append(instance.category.id)
        return path_ids

    def prepare_location_path(self, instance):
        path_ids = list(get_parent_ids(instance.location))
        path_ids.append(instance.location.id)
        return path_ids

    def prepare_user(self, instance):
        return PublicUserSerializer(instance.user).data

    def prepare_like_count(self, instance):
        return instance.likes.count()

    def prepare_favorite_count(self, instance):
        return instance.favorites.count()

    def prepare_parameters(self, instance):
        return ProductParameterSerializer(instance.parameters.all(), many=True).data

    def prepare_contacts(self, instance):
        return ProductContactSerializer(instance.contacts.all(), many=True).data

    def prepare_location(self, instance):
        return ChildLocationSerializer(instance.location).data

    def prepare_photos(self, instance):
        photos = []
        for i in instance.photos.iterator():
            data = {
                'id': i.pk,
                'photo': i.photo.name,
                'small_thumbnail': i.small_thumbnail.name,
                'medium_thumbnail': i.medium_thumbnail.name
            }
            photos.append(data)
        return photos

    def get_queryset(self):
        return super().get_queryset().select_related(
            'user', 'category', "user__business"
        )

    def get_instances_from_related(self, related_instance):
        """
        Reindexing all products that are defined  Django inner class attribute related_models
        """
        if isinstance(related_instance, User):
            return related_instance.products.all()
        elif isinstance(related_instance, ProductPhoto):
            return related_instance.product
        elif isinstance(related_instance, ProductContact):
            return related_instance.product
        elif isinstance(related_instance, ProductParameter):
            return related_instance.product
        elif isinstance(related_instance, Location):
            return related_instance.products.all()
