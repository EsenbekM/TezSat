from django.db import connection


def get_product_stats_by_user(user_id):
    sql = '''
    select
        sum(p.show_count) as show_count,
        sum(p.view_count) as view_count,
        sum(p.call_count) as call_count,
        sum(p.message_count) as message_count,
        (
            select count(*) from user_favorites uf
            where uf.product_id in (select id from product where user_id={user_id})
        ) as favorite_count,
        (
            select count(*) from product_review pr
            where pr.product_id in (select id from product where user_id={user_id})
        ) as review_count,
        (
            select count(*) from user_likes ul
            where ul.product_id in (select id from product where user_id={user_id})
        ) as like_count
    from product as p
    where p.user_id={user_id} and p.state in ('active', 'on_review')
            '''.format(user_id=user_id)
    with connection.cursor() as cursor:
        cursor.execute(sql)
        row = cursor.fetchone()
    show_count, view_count, call_count, message_count, favorite_count, review_count, like_count = row
    return {
        "show_count": show_count or 0,
        "view_count": view_count or 0,
        "call_count": call_count or 0,
        "message_count": message_count or 0,
        "favorite_count": favorite_count or 0,
        "review_count": review_count or 0,
        "like_count": like_count or 0,
        "coverage": view_count or 0
    }
    # select
    #     sum(p.show_count) as show_count,
    #     sum(p.view_count) as view_count,
    #     sum(p.call_count) as call_count,
    #     sum(p.message_count) as message_count,
    #     (
    #         select count(*) from user_favorites uf
    #         where uf.product_id in (select id from product where user_id={user_id})
    #     ) as favorite_count,
    #     (
    #         select count(*) from product_review pr
    #         where pr.product_id in (select id from product where user_id={user_id})
    #     ) as review_count,
    #     (
    #         select count(*) from user_likes ul
    #         where ul.product_id in (select id from product where user_id={user_id})
    #     ) as like_count
    # from product as p
    # where p.user_id={user_id}

# select
#     p.*,
#     count(uf) as favorite_count,
#     count(pr) as review_count,
#     count(ul) as like_count
# from product as p
# left join user_favorites uf on p.id = uf.product_id
# left join product_review pr on p.id = pr.product_id
# left join user_likes ul on p.id = ul.product_id
#
# where p.user_id = 1
# group by p.id, p.show_count, p.view_count, p.call_count, p.message_count
