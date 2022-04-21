from uuid import uuid4

from django_elasticsearch_dsl import Document, fields, Index
from django_elasticsearch_dsl.registries import registry
from elasticsearch_dsl import analyzer, token_filter, Completion

from category.models import Category
from product.models import Keyword

autocomplete = Index('autocomplete')
autocomplete.settings(
    number_of_shards=3,
    number_of_replicas=0
)


class CompletionField(fields.DEDField, Completion):
    pass


shingle = analyzer(
    "shingle",
    type="custom",
    tokenizer="standard",
    filters=[
        "standard",
        "lowercase",
        "shingle",
        token_filter('russian_stop', 'stop', stopwords='_russian_'),
    ]
)


@registry.register_document
@autocomplete.document
class AutocompleteCategory(Document):
    id = fields.KeywordField()
    title = fields.TextField()
    title_suggest = CompletionField()
    is_category = fields.BooleanField()

    class Django:
        model = Category
        ignore_signals = True

    @classmethod
    def generate_id(cls, object_instance):
        """
        Generating uuid4 ids instead of Django's default instance.pk to avoid overriding objects id in elasticsearch
        """
        return uuid4()

    def prepare_is_category(self, instance):
        return True

    def prepare_title(self, instance):
        if 'title_ru' in vars(instance):
            return instance.title_ru
        if 'title_ky' in vars(instance):
            return instance.title_ky

    def prepare_title_suggest(self, instance):
        if 'title_ru' in vars(instance):
            return f"{instance.title_ru}"
        if 'title_ky' in vars(instance):
            return f"{instance.title_ky}"

    def get_queryset(self):
        q1 = Category.objects.only('title_ky', 'id', 'parent')
        q2 = Category.objects.only('title_ru', 'id', 'parent')
        return q1.union(q2, all=True)


@registry.register_document
@autocomplete.document
class ProductKeyword(Document):
    id = fields.KeywordField()
    title = fields.TextField()
    title_suggest = CompletionField()
    is_category = fields.BooleanField()

    class Django:
        model = Keyword
        ignore_signals = True

    def get_queryset(self):
        qs = super(ProductKeyword, self).get_queryset().filter(is_search=False)
        return qs

    def prepare_title(self, instance):
        return instance.keyword

    def prepare_title_suggest(self, instance):
        return self.prepare_title(instance)

    def prepare_is_category(self, instance):
        return False
