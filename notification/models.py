from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _
from django_q.models import Schedule

from .settings import NotificationAction

User = get_user_model()


class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender_notifications', null=True)
    product = models.ForeignKey('product.Product', on_delete=models.CASCADE, null=True)
    title_ky = models.CharField('title', max_length=100, null=True, blank=True)
    title_ru = models.CharField('title', max_length=100, null=True, blank=True)
    description_ky = models.CharField('description', max_length=500, null=True, blank=True)
    description_ru = models.CharField('description', max_length=500, null=True, blank=True)
    action = models.CharField('action', max_length=200, choices=NotificationAction.choices(), null=False)
    creation_date = models.DateTimeField('creation_date', auto_now_add=True)
    is_read = models.BooleanField('is read', default=False, null=False)


class PushNotification(models.Model):
    """
    Class allowing admin users to create instances of it and send push
     notification to registered users with fmc_id.
    """

    class Meta:
        db_table = 'push_notification'

    title_ru = models.CharField(_('title in russian'), null=False, max_length=200)
    title_ky = models.CharField(_('title in kyrgyz'), null=False, max_length=200)
    message_ru = models.TextField(_('message in russian'), null=True, blank=True)
    message_ky = models.TextField(_('message in kyrgyz'), null=True, blank=True)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    location = models.ForeignKey('location.Location', null=True, blank=True, on_delete=models.CASCADE)
    user_chunk = models.PositiveIntegerField(default=5000)
    notified_users = models.PositiveIntegerField(default=0)
    minutes = models.PositiveIntegerField(_('interval in minutes'), default=60)
    business = models.CharField(_('selection'), max_length=50, choices=NotificationAction.push_choices(), null=False)

    def _partial_notification(self):
        """
        Creating django_q scheduled task for notification of users by chunk
         specified in PushNotification.
        """
        scheduled_task = Schedule(
            name="partial-user-notification",
            args=f"{self.id}",
            func='notification.services.chunk_notification',
            schedule_type=Schedule.MINUTES,
            minutes=self.minutes,
        )
        scheduled_task.save()

    def save(self, *args, **kwargs):
        if not self.pk:
            super(PushNotification, self).save(*args, **kwargs)
            self._partial_notification()
            return
        super(PushNotification, self).save(*args, **kwargs)

    def __str__(self):
        return self.title_ru
