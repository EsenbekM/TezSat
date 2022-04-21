import pytest

from category.models import Category
from category.services import save_slug
from users.services import get_translit_word


@pytest.mark.parametrize(
    'word, translit', [
        ('Небо', 'nebo'),
        ('Недвижимость', 'nedvizhimost'),
        ('ёжик', 'yozhik'),
        ('гонъ', 'gon'),
        ('mazda', 'mazda'),
        ('noutbook, computer', 'noutbook computer'),
        ('noutbook computer', 'noutbook computer')
    ]
)
def test_word_translit(word, translit):
    new_translit = get_translit_word(word)

    assert new_translit == translit


@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, title_slug', [
        ("недвижимость", "nedvizhimost"),
        ('грузовые машины', 'gruzovye-mashiny'),
        ('mazda', 'mazda'),
        ('rolls royce', 'rolls-royce'),
        ('подъезд', 'podezd'),
    ]
)

def test_category(title, title_slug):
    category = Category.objects.create(title_ru=title, title_ky=title)
    save_slug()
    category.refresh_from_db()
    assert category.title_slug == title_slug

@pytest.mark.django_db
@pytest.mark.parametrize(
    'title, title_slug, parent', [
        ("другое", "drugoe", ''),
        ('грузовые машины', 'gruzovye-mashiny', ''),
        ('mazda', 'mazda', ''),
        ('другое', 'mashina-drugoe', "машина"),
        ('другое', 'avto-drugoe', "авто"),
    ]
)

def test_slug(title, title_slug, parent):
    parent_category = None
    if title == "другое" and parent:
        parent_category = Category.objects.create(title_ru=parent, title_ky=parent)
    category = Category.objects.create(title_ru=title, title_ky=title, parent=parent_category)
    save_slug()
    category.refresh_from_db()
    assert category.title_slug == title_slug