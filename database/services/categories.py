from database.models import Categories, CategoriesMultiLang, Users, Post, Pictures, Patterns
from database.services.session import SessionWork as session


def get_category_parents_ids(child_id: int, chat_id: int):
    if category := Categories.get_or_none(Categories.id == child_id):

        if temp_category := CategoriesMultiLang.get_or_none(category=Categories.get(Categories.id == child_id),
                                                            language=session.get_lang_code(chat_id=chat_id)):
            category_title = temp_category.title
        else:
            category_title = CategoriesMultiLang.get(category=Categories.get(Categories.id == child_id),
                                                     language=1).title

        categories = ['<b>' + category_title + '</b>', ]

        if parent_id := category.parent_id:
            categories += get_category_parents_ids(child_id=parent_id,
                                                   chat_id=chat_id)
        return categories


def get_all_child_categories(category_id: int) -> list[int]:
    """
        Поиск всех дочерних категорий
    :param category_id: родительская категория
    :return: список категорий с айдишниками
    """
    if categories := Categories.select().where(Categories.parent_id == category_id):
        all_categories = []
        for category in categories:
            all_categories += get_all_child_categories(category_id=category.id)
        return all_categories
    else:
        return [category_id, ]


def change_category_parent_id(chat_id: int, parent_id: int = None):
    """
        Изменение категории родителя который просматриваетмся юзером
    :param chat_id:
    :param parent_id:
    :return:
    """
    if parent_id != -1:
        user: Users = Users.get(Users.id == chat_id)
        user.session['category_parent_id'] = parent_id
        user.save()
    else:
        return Users.get(Users.id == chat_id).session['category_parent_id']


def get_category_by_id_for_parent_id(category_id: int) -> int:
    return Categories.get_by_id(category_id).parent_id


def get_category_by_id(category_id: int,
                       chat_id: int) -> str:

    if category := CategoriesMultiLang.get_or_none(category=Categories.get_by_id(category_id),
                                                   language=session.get_lang_code(chat_id=chat_id)):
        return category.title

    else:
        return CategoriesMultiLang.get_or_none(category=Categories.get_by_id(category_id),
                                               language=1).title


def get_categories(chat_id: int,
                   pattern_id: int,
                   parent_id: int = None,) -> tuple[tuple]:

    # pattern = Patterns.get_by_id(pattern_id)

    query = CategoriesMultiLang \
        .select(Categories.id,
                CategoriesMultiLang.title) \
        .join(Categories) \
        .where((Categories.parent_id == parent_id) &
               (Categories.pattern_id == pattern_id))

    if session.get_lang_code(chat_id=chat_id) == 2:
        query = query.order_by(CategoriesMultiLang.language.desc())
        query = query.select(Categories.id,
                             CategoriesMultiLang.title,
                             CategoriesMultiLang.language)
        query = list(query.tuples())
        ids_in_sorted = []
        sorted_ = []
        for row in query:
            if row[0] not in ids_in_sorted:
                sorted_.append(row[:2])
                ids_in_sorted.append(row[0])
        return tuple(sorted_)

    else:
        query = query\
            .where((Categories.parent_id == parent_id) &
                   (Categories.pattern_id == pattern_id) &
                   (CategoriesMultiLang.language == 1))
        return tuple(query.tuples())


def add_category(pattern_id: str,
                 parent_id: str,
                 new_category: dict) -> bool:

    title_rus, title_uzb = new_category['title_rus'], new_category['title_uzb']

    if not CategoriesMultiLang\
            .select()\
            .join(Categories)\
            .where(CategoriesMultiLang.title.in_((title_rus, title_uzb)) &
                   (CategoriesMultiLang.category.pattern_id == pattern_id)):

        category = Categories(parent_id=parent_id,
                              pattern_id=pattern_id,
                              status=new_category['status'],
                              buy_status=new_category['buy_status'])
        category.save()
        CategoriesMultiLang(category=category,
                            language=1,
                            title=title_rus).save()
        CategoriesMultiLang(category=category,
                            language=2,
                            title=title_uzb).save()
        return True


def change_category(parent_id: str, rus_title: str, uzb_title: str):
    category: Categories = Categories.get(Categories.id == parent_id)

    rus_category = CategoriesMultiLang.get(category=category,
                                           language=1)
    rus_category.title = rus_title
    rus_category.save()

    if uzb_category := CategoriesMultiLang.get_or_none(category=category,
                                                       language=2):
        uzb_category.title = uzb_title
        uzb_category.save()

    else:
        CategoriesMultiLang(category=category,
                            language=2,
                            title=uzb_title).save()


def remove_category(parent_id: str):
    Post.delete().where(Post.category_id == parent_id)
    Categories.get(Categories.id == parent_id).delete_instance()


def get_child_categories(parent_id: str) -> tuple[Categories]:
    return Categories\
        .select()\
        .where(Categories.parent_id == parent_id)


def get_categories_ids_by_pattern_id(pattern_id: str):
    return tuple(Categories
                 .select(Categories.id)
                 .where(Categories.pattern_id == pattern_id)
                 .tuples())


def exists_status(category_id: str) -> bool:
    """
        Существует ли у категории статус
    """
    return Categories.get_by_id(category_id).status


def exists_buy_status(category_id: str) -> bool:
    """
        Существует ли у категории фильтр купить / продать
    """
    return Categories.get_by_id(category_id).buy_status