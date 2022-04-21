from django.contrib.auth import get_user_model
from django_q.models import Schedule

from notification.models import PushNotification
from notification.settings import NotificationAction
from tezsat.settings import Lang

User = get_user_model()


def chunk_notification(push_id):
    pn = PushNotification.objects.get(id=int(push_id))
    start = pn.notified_users
    end = pn.notified_users + pn.user_chunk
    qs = User.objects.filter(fcm_id__isnull=False).order_by('-id')
    if pn.business == NotificationAction.BUSINESS:
        qs = qs.filter(business__is_active=True)
    elif pn.business == NotificationAction.REGULAR_USER:
        qs = qs.filter(business__is_active=False)
    if qs.count() <= end:
        end = qs.count()
        schedule = Schedule.objects.get(args__exact=push_id)
        schedule.delete()
    qs = qs[start:end]
    for user in qs.iterator():
        try:
            if user.language == Lang.KY:
                user.send_message(title=pn.title_ky, body=pn.message_ky)
            else:
                user.send_message(title=pn.title_ru, body=pn.message_ru)
        except Exception:
            pass
    pn.notified_users = end
    pn.save()
