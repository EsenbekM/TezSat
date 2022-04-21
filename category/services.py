from category.models import Category
from users.services import get_translit_word


def save_slug():
    categories = Category.objects.all()
    for i in categories:
        if i.title_ru.lower() == "другое" and i.parent:
            p = i.parent.title_ru
            word = get_translit_word(i.title_ru, parent=p)
        else:
            word = get_translit_word(i.title_ru)
        word = word.replace(" ", "-")
        i.title_slug = word
        i.save()
