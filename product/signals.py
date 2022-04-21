from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import ProductReview
from .jobs import calculate_product_rating


@receiver(post_save, sender=ProductReview)
def post_save_review(sender, **kwargs):
    calculate_product_rating(kwargs['instance'].product)


@receiver(post_delete, sender=ProductReview)
def post_delete_review(sender, **kwargs):
    calculate_product_rating(kwargs['instance'].product)
