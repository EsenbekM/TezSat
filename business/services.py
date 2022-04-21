import datetime
from datetime import datetime as dt

from django.db.models import Count, Q

from product.models import Product
from users.models import User
from .models import BusinessSchedule, BusinessStatistics as BS
from .settings import Week


def create_business_extra(data, business, model):
    model.objects.filter(business=business).delete()
    for i in data:
        model.objects.create(**i, business=business)


def create_schedules(data, business):
    schedules = []
    for i in data:
        try:
            schedule = BusinessSchedule.objects.get(weekday=i['weekday'], business=business)
            schedule.time = i['time']
            schedules.append(schedule)
        except Exception:
            BusinessSchedule.objects.create(**i, business=business)

    if schedules:
        BusinessSchedule.objects.bulk_update(schedules, ['time'])


def business_admin_statistics(start_date, end_date, business_id):
    date_range = _prepare_date_range(start_date, end_date)

    statistics = BS.objects.filter(product__user__business__id=business_id)
    statistics = statistics. \
        filter(*date_range)

    statistics = statistics.values("date"). \
        annotate(click_count=Count('stats_type', filter=Q(stats_type=BS.CLICK))). \
        annotate(view_count=Count('stats_type', filter=Q(stats_type=BS.VIEW))). \
        annotate(call_count=Count('stats_type', filter=Q(stats_type=BS.CALL))). \
        annotate(message_count=Count('stats_type', filter=Q(stats_type=BS.MESSAGE)))

    statistics = _order_statistics(statistics, business_id, start_date)
    return statistics


def business_stats(product_id, start_date, end_date, user_id=None):
    date_range = _prepare_date_range(start_date, end_date)
    if not start_date:
        date_range = []
        now = dt.now().date()
        start_date = now - datetime.timedelta(days=7)
        date_range.append(Q(date__gte=start_date))
        date_range.append(Q(date__lte=now))
    if user_id:
        statistics = BS.objects.filter(product__user_id=user_id)

    if product_id:
        statistics = BS.objects.filter(product_id=product_id)
    try:
        s_d = statistics.order_by('id').first().date
        s_d = datetime.datetime(year=s_d.year, month=s_d.month, day=s_d.day,
                                hour=1, minute=1, second=1)
        start_date = int(datetime.datetime.timestamp(s_d))
    except AttributeError:
        start_date = 0

    statistics = statistics. \
        filter(*date_range)

    user = User.objects.filter(products__id=product_id).first()
    user_id = user.id if user else None
    statistics = statistics.values("date"). \
        annotate(click_count=Count('stats_type', filter=Q(stats_type=BS.CLICK))). \
        annotate(view_count=Count('stats_type', filter=Q(stats_type=BS.VIEW))). \
        annotate(call_count=Count('stats_type', filter=Q(stats_type=BS.CALL))). \
        annotate(message_count=Count('stats_type', filter=Q(stats_type=BS.MESSAGE)))

    statistics = _order_statistics(statistics, user_id, start_date)
    return statistics


def _prepare_date_range(start_date, end_date):
    date_range = []
    if not start_date:
        pass
    else:
        start = datetime.date.fromtimestamp(int(start_date))
        date_range.append(Q(date__gte=start))

    if not end_date:
        end_date = datetime.date.today()
    else:
        end_date = datetime.date.fromtimestamp(int(end_date))

    date_range.append(Q(date__lte=end_date))
    return date_range


def _order_statistics(stats, user_id, start_date):
    ordered_stats = {
        "click_count": [],
        "view_count": [],
        "call_count": [],
        "message_count": [],
    }
    for stat in stats:
        for key in ordered_stats.keys():
            ordered_stats[key].append(
                {
                    'date': str(stat['date']),
                    'count': stat[key]
                }
            )
    ordered_stats['user_id'] = user_id
    ordered_stats['start_date'] = start_date
    return ordered_stats


def record_statistics(product_ids, stats_type):
    date = datetime.date.today()
    products = Product.objects.filter(id__in=product_ids).filter(user__business__isnull=False). \
        filter(user__business__is_active=True)
    for product in products:
        BS.objects.create(date=date, stats_type=stats_type, product=product)


def order_weekday(schedule):
    weekday = [i[0] for i in Week.choices()]
    s = [schedule.filter(weekday=i)[0] for i in weekday if i in schedule.values_list('weekday', flat=True)]
    return s


def date_in(now, creation_date, end):
    date1 = [(creation_date + (datetime.timedelta(days=10) * i)).date() for i in range(1, 6)]
    date2 = [(end - datetime.timedelta(days=x)).date() for x in range(1, 8)]
    # n = datetime.datetime(year=2021, month=8, day=16).date()
    if now.date() in [creation_date.date(), *date1, *date2]:
        return True
    return False
