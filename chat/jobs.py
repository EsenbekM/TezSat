from django_q.tasks import async_task

from business.models import BusinessStatistics
from business.services import record_statistics


def new_message(sender, receiver, product, message):
    async_task(record_statistics, [product.id], BusinessStatistics.MESSAGE)
    receiver.push_new_message(sender, message, data={
        "buyer": str(sender.id),
        "seller": str(receiver.id),
        "product_id": str(product.id),
    })
