from django.db import models
from django.utils.translation import gettext_lazy as _

from product.models import Product
from .settings import ICON_UPLOAD_DIR, ParameterType


class Category(models.Model):
    class Meta:
        db_table = 'category'
        verbose_name_plural = "categories"
        ordering = ('order',)

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    title_ru = models.CharField(_('title in russian'), max_length=50, null=False)
    title_ky = models.CharField(_('title in kyrgyz'), max_length=50, null=False)
    title_slug = models.CharField(_('slug'), max_length=50, null=True)
    icon = models.ImageField(_('icon'), upload_to=ICON_UPLOAD_DIR, null=True, blank=True)
    large_icon = models.ImageField(_('large icon'), upload_to=ICON_UPLOAD_DIR, null=True, blank=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def _get_parameters(self, category, params):
        params += category.parameters.all()
        if category.parent is None:
            return params
        else:
            return self._get_parameters(category.parent, params)

    def get_parameters(self):
        params = []
        self._get_parameters(self, params)
        return params

    def __str__(self):
        return self.title_ru
        # return get_recursive_title(Category, self.id, 'ru')

    def product_count(self):
        return Product.objects.filter(category=self).count()

class CategoryFixture(Category):
    class Meta:
        verbose_name = 'Parent category'
        verbose_name_plural = 'Parents category'
        proxy = True
        ordering = ('order',)


class Parameter(models.Model):
    class Meta:
        db_table = 'parameter'
        ordering = ('order',)

    category = models.ForeignKey('Category', on_delete=models.CASCADE, related_name='parameters')
    type = models.CharField(_('type'), max_length=50, null=False, default=ParameterType.SELECT,
                            choices=ParameterType.choices())
    is_many = models.BooleanField(_('is many'), default=False)
    title_ru = models.CharField(_('title in russian'), max_length=50, null=False)
    title_ky = models.CharField(_('title in kyrgyz'), max_length=50, null=False)
    optional = models.BooleanField(_('optional'), default=True)
    order = models.PositiveIntegerField(default=0, blank=False, null=False)

    def __str__(self):
        return str(self.title_ru)


class Option(models.Model):
    class Meta:
        db_table = 'option'

    parameter = models.ForeignKey('Parameter', on_delete=models.CASCADE, related_name='options')
    title_ru = models.CharField(_('title in russian'), max_length=50, null=False)
    title_ky = models.CharField(_('title in kyrgyz'), max_length=50, null=False)

    def __str__(self):
        return str(self.title_ru)
