from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl.signals import RealTimeSignalProcessor
from django_q.tasks import async_task


class AsyncSignalProcessor(RealTimeSignalProcessor):
    """
    Default django_dls signal processor function wrapped in async_task()
    """

    def handle_save(self, sender, instance, **kwargs):
        """
        Handle save.
        """
        async_task(registry.update, instance, task_name="handle-save-signal")
        async_task(registry.update_related, instance, task_name="handle-related-save-signal")

    def handle_pre_delete(self, sender, instance, **kwargs):
        """
        Handle removing of instance object from related models instance.
        """
        async_task(registry.delete_related, instance, task_name='handle-pre-delete-signal')

    def handle_delete(self, sender, instance, **kwargs):
        """
        Handle delete.
        """
        async_task(registry.delete, instance, raise_on_error=False, task_name='handle-delete-signal')
