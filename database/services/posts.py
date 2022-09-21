import os

from database.services.patterns import get_pattern_questions
from database.services.session import SessionWork as session
from database.config import Constants
from database.models import Post, KeyWord, Pictures, Users, ProductProps, PatternProps
from database.services.categories import get_all_child_categories
from database.services.settings import get_setting
# from bot.util import bot
from global_var import CHANNEL_ID_62
from bot.services.output_posts import format_post_from_dict


def get_posts_by_keywords(keywords: list):
    return Post \
        .select() \
        .join(Post.keywords.get_through_model()) \
        .join(KeyWord) \
        .filter(KeyWord.word.in_(keywords))


def post_all() -> tuple[Post]:
    posts = Post.select().where(Post.moderate == True)
    Post.update({Post.active: True,
                 Post.moderate: False}) \
        .where(Post.moderate == True).execute()
    return posts


def get_post_amount_from_city_id(categories: list, city_id: str = None) -> str:
    return '[' + str(len(Post
                         .select()
                         .where(((Post.city == city_id) if city_id else 1) &
                                (Post.active == True) &
                                (Post.category_id.in_(categories))))) + ']'


def upload_photo(photos: list) -> list:
    """
        Загрузка фотографий из папки в базу и удаление их потом
    :param photos: список, имена фотографий
    :return: список, айдишники фоток
    """
    photos_ids = []
    for photo in photos:
        with open(photo, 'rb') as file:
            picture = Pictures(image=file.read())
            picture.save()
            photos_ids.append(picture)
        os.remove(photo)
    return photos_ids


def upload_words(words: list) -> list:
    """
        Загрузка фотографий из папки в базу и удаление их потом
    :param photos: список, имена фотографий
    :return: список, айдишники фоток
    """
    result_words = []
    for word in words:
        new_word = KeyWord.get_or_none(word=word)
        if not new_word:
            new_word = KeyWord(word=word)
            new_word.save()
        result_words.append(new_word)
    return result_words


def setup_product(post_data: dict, pattern_id: str, post: Post):
    for prop in get_pattern_questions(pattern_id=pattern_id):
        type_, *other_args = prop[1].split('_')

        if type_ in ('text', 'int', 'contact'):
            ProductProps(product=post,
                         prop=PatternProps.get_by_id(prop[0]),
                         value=post_data[str(prop[0])]).save()

        # elif type_ == 'photo':
        #     bot.send_media_group(chat_id=chat_id,
        #                          media=get_photos_from_dict(photos=post_value))
        #
        # elif type_ == 'geo':
        #     long, lati = post_value
        #     markup = markups.get_geo(chat_id=chat_id,
        #                              long=long,
        #                              lati=lati)


def get_modereate_status():
    return get_setting(setting_id=Constants.Settings.MODERATE_STATUS)


def publicate_post(chat_id: int) -> bool:
    """
        Метод в котором происходит занос поста в базу
    :param chat_id: идентификатор пользователя для просмотра его сесси в которой все данные
    :return: булевое значение, на модерации ли пост или нет
    """
    user: Users = Users.get(Users.id == chat_id)
    user.available_posts -= 1
    post_data = user.session['post']
    moderate_status = get_modereate_status()
    geo = post_data.get('geo')

    post = Post(category_id=post_data['category_id'],
                moderate=moderate_status,
                owner=chat_id,
                status=post_data.get('status'),
                city=user.city,
                chosen_channels=post_data['selected_channels'],
                currency=post_data['currency'],
                buy_status=post_data['buy_status'],
                **geo
                )
    post.save()

    # photos = upload_photo(photos=list(post_data[key] for key in post_data if key.endswith('photo')))
    if 'photos' in post_data:
        photos = upload_photo(photos=post_data['photos'])
        post.pictures.add(photos)

    words = upload_words(words=post_data['keywords'])
    if words:
        post.keywords.add(words)

    user.save()

    setup_product(post_data=post_data,
                  pattern_id=user.session['pattern_id'],
                  post=post)

    return bool(moderate_status)


def get_post_by_category(category_id: str) -> tuple[Post]:
    return Post \
        .select() \
        .where((Post.category_id == category_id) &
               (Post.active == True) &
               (Post.deleted == False) &
               (Post.moderate == False))


def get_post_by_category_with_parent(category_id: str,
                                     city: str = None,
                                     product_status: int = None,
                                     buy_status: bool = False):
    categories_ids = get_all_child_categories(category_id=category_id) + [category_id, ]
    return Post \
        .select() \
        .where((Post.category_id.in_(categories_ids)) &
               (Post.active == True) &
               (Post.deleted == False) &
               (Post.moderate == False) &
               ((Post.city == city) if city else True) &
               ((Post.status == product_status) if product_status is not None else True) &
               (Post.buy_status == buy_status))


def get_post_by_category_and_status(category_id: str,
                                    chat_id: int) -> tuple[Post]:
    city = session.get(chat_id=chat_id,
                       key='search_city')
    product_status = session.get(chat_id=chat_id,
                                 key='search_status')
    buy_status = session.get(chat_id=chat_id,
                             key='search_buy_status')
    return get_post_by_category_with_parent(category_id=category_id,
                                            city=city,
                                            product_status=product_status,
                                            buy_status=buy_status)


def get_left_and_right_post_id(category_id: str,
                               post_id: int,
                               chat_id: int) -> tuple[int, int, tuple]:
    city = session.get(chat_id=chat_id,
                       key='search_city')
    status = session.get(chat_id=chat_id,
                         key='search_status')
    buy_status = session.get(chat_id=chat_id,
                             key='search_buy_status')
    # categories_ids = get_all_child_categories(category_id=category_id)

    posts = get_post_by_category_with_parent(category_id=category_id,
                                             city=city,
                                             product_status=status,
                                             buy_status=buy_status)

    posts_ids = [post.id for post in posts][::-1]
    current_post = posts_ids.index(post_id)

    if current_post >= Constants.AMOUNT_POSTS_TO_CUS:
        prev_index = current_post - Constants.AMOUNT_POSTS_TO_CUS
    else:
        prev_index = -1

    if current_post + Constants.AMOUNT_POSTS_TO_CUS < len(posts_ids):
        next_index = current_post + Constants.AMOUNT_POSTS_TO_CUS
    else:
        next_index = -1

    return next_index, prev_index, posts[current_post: current_post + Constants.AMOUNT_POSTS_TO_CUS]


def get_post_by_id(post_id: str) -> Post:
    return Post.get(Post.id == post_id)


def get_moderation_posts(chat_id: int = 0) -> tuple:
    """
    :param chat_id: для вывода одному человеку
                    (если пользователя интересуют посты которые сейчас на модерации)
    :return:
    """
    return Post \
        .select() \
        .where(((Post.owner == chat_id) if chat_id else True) &
               (Post.moderate == True))


def get_active_posts(chat_id: int = 0) -> tuple:
    return Post \
        .select() \
        .where(((Post.owner == chat_id) if chat_id else True) &
               (Post.active == True))


def get_deleted_posts(chat_id: int = 0) -> tuple:
    return Post \
        .select() \
        .where(((Post.owner == chat_id) if chat_id else True) &
               (Post.deleted == True))


def activate_post(post_id: int) -> tuple[int, str]:
    post = Post.get_by_id(post_id)
    post.moderate = False
    post.active = True
    post.deleted = False
    post.owner.amount_posts += 1
    post.save()

    return post.owner, post.id


def delete_post(post_id: int, cause: str) -> tuple[int, str]:
    """
        Удаление поста
    :param post_id: айди поста
    :param cause: причина удаления
    :return:
    """
    post = Post.get_by_id(post_id)
    post.moderate = False
    post.active = False
    post.deleted = True
    post.description_claim = cause
    post.owner.amount_warnings += 1
    post.save()
    post.owner.save()
    return post.owner, post.id


# Test delete post
def post_delete(post_id: int):
    post = Post.get_by_id(post_id)
    post.moderate = False
    post.active = False
    post.deleted = True
    post.owner.amount_posts -= 1
    post.save()
    return post.id


def change_post(post_id: int, cause: str, description: str = '', title: str = '', price: str = '') -> tuple[int, str]:
    """
        Удаление поста
    :param title: название поста
    :param price: цена поста
    :param description: новое описание
    :param post_id: айди поста
    :param cause: причина изменения
    :return:
    """
    post = Post.get_by_id(post_id)
    post.moderate = False
    post.active = True
    post.deleted = False
    # if description:
    #     post.description = description
    # if title:
    #     post.title = title
    # if price:
    #     post.price = price
    post.description_claim = cause
    post.owner.amount_warnings += 1
    post.owner.amount_posts += 1
    post.save()
    post.owner.save()
    return post.owner, post.id


def get_amount_posts_in_category(category_id: int, city: str) -> str:
    return '[' \
           + str(len(get_post_by_category_with_parent(category_id=str(category_id),
                                                      city=city))) \
           + ']'


def get_location(post_id: str) -> tuple:
    post: Post = Post.get_by_id(post_id)
    return post.longitude, post.latitude


if __name__ == '__main__':
    # print(get_posts_by_keywords(['привет', 'прикол']))
    # for i in get_posts_by_keywords(['привет', 'прикол']):
    #     print(i)
    ...


def get_posts_list_with_id(contains: str):
    return tuple(Post
                 .select(Post.id,
                         Post.owner_id,
                         Post.city)
                 .filter((Post.id.contains(contains)) & (Post.active == True))
                 .tuples())


# Test
def get_own_posts_list_with_id(contains: str, chat_id: int):
    return tuple(Post
                 .select(Post.id,
                         Post.owner_id,
                         Post.city)
                 .filter((Post.active == True) & (Post.owner == chat_id) & (Post.id.contains(contains)))
                 .tuples())


def get_posts_list(status: str):
    if status == Constants.STATUSES[3]:
        statuses = Constants.STATUSES[:3]

    elif status == Constants.STATUSES[4]:
        statuses = Constants.STATUSES[:4]

    else:
        statuses = Constants.STATUSES[:]

    return tuple(Post
                 .select(Post.id,
                         Post.owner_id,
                         Post.city)
                 .where(Post.status in statuses)
                 .tuples())


def get_own_posts_list(status: str, chat_id: int):
    if status == Constants.STATUSES[3]:
        statuses = Constants.STATUSES[:3]

    elif status == Constants.STATUSES[4]:
        statuses = Constants.STATUSES[:4]

    else:
        statuses = Constants.STATUSES[:]

    return tuple(Post
                 .select(Post.id,
                         Post.owner_id,
                         Post.city)
                 .where((Post.status in statuses) & (Post.owner == chat_id) & (Post.active == True))
                 .tuples())


def get_post_data(id: int) -> Post:
    """
        Получение поста и его данных из бд в виде объекта\
    :param id : айди поста
    :return: объект post
    """
    return Post.get(Post.id == id)


def get_users_posts(owner_id: int) -> Post:
    """
        Получение постов определённого пользователя для удаления или редактирования
    """

    return Post.select().where((Post.active == True) & (Post.owner == owner_id))
