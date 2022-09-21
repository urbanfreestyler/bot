from bot.services.output_posts import output_posts
from bot.util import *
from database.models import Post, Categories
from bot.general_controllers import start_bot


@bot.message_handler(commands=Commands.SEARCH)
@bot.message_handler(func=partial(message_data_handler, 'Buttons.WATCH_POSTS'))
@get_message_info
def choise_search_type(chat_id: int, *args):

    logger.info(f'User {chat_id} search posts')
    send_message(chat_id=chat_id,
                 text_id='SetSearchType',
                 reply_markup=markups.get_search_types(chat_id=chat_id))


@bot.message_handler(func=partial(message_data_handler, "Buttons.SearchByCategories"))
@get_message_info
def watch_posts(chat_id: int, *args):

    send_message(chat_id=chat_id,
                 text_id='ChoisePattern',
                 reply_markup=markups.patterns(chat_id=chat_id, search=True))


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.PatternSearchPost))
@get_message_info(callback=Callbacks.PatternSearchPost)
def set_pattern(chat_id: int, text: str, *args):

    if len(args):
        delete_message(chat_id=chat_id,
                       message_id=args[0])

        if text == 'back':
            start_bot(chat_id=chat_id)
            return

        else:
            session.set(chat_id=chat_id,
                        key='pattern_id',
                        value=text)

    get_search_city(chat_id=chat_id)


def get_search_city(chat_id: int):
    send_message(chat_id=chat_id,
                 text_id="BotMessages.PostForCustomers.GET_CITY",
                 reply_markup=markups.get_city_for_search(back_=True,
                                                          chat_id=chat_id))


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.SEARCH_CITY))
@get_message_info(callback=Callbacks.SEARCH_CITY)
def set_search_city(chat_id: int, text: str, message_id: int):

    delete_message(chat_id=chat_id,
                   message_id=message_id)

    if text == 'back':
        watch_posts(chat_id=chat_id)
        return

    else:
        session.set(chat_id=chat_id,
                    key='search_city',
                    value=text if text != 'all' else None)

    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id, text_id="BotMessages.PostCheck.INPUT_NEED_CATEGORY"),
                 reply_markup=markups.categories(chat_id=chat_id))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.CATEGORY[:-2]) and
                                                  not session.get(chat_id=callback.from_user.id,
                                                                  key='add_post'))
@get_message_info(callback=Callbacks.CATEGORY)
def get_category(chat_id: int, text: str, message_id: int):

    markup = ''

    category_parent_id = session.get(chat_id=chat_id,
                                     key='category_parent_id')

    if text == 'back':
        # нажали кнопку назад в категориях

        if current_parent_category := category_parent_id:
            # если есть родитель, и нажали кнопку назад, выводим категории родителя родителя

            parent_id = db_util.get_category_by_id_for_parent_id(category_id=current_parent_category)

            session.set(chat_id=chat_id,
                        key='category_parent_id',
                        value=parent_id)

            edit_callback_message(chat_id=chat_id,
                                  message_id=message_id,
                                  reply_markup=markups.categories(parent_id=parent_id,
                                                                  chat_id=chat_id))
        else:
            # если нет родительских категорий, выходим к шаблонам

            delete_message(chat_id=chat_id,
                           message_id=message_id)
            watch_posts(chat_id=chat_id)

    elif text.split('_')[0] in (Callbacks.Direction.LEFT, Callbacks.Direction.RIGHT):
        # песли листаем список с категориями

        offset = int(text.split('_')[-1])

        markup = markups.categories(offset=offset,
                                    parent_id=category_parent_id,
                                    chat_id=chat_id)

        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=markup)

    else:
        # если выбрали категорию

        if text == "all":
            category_parent_id = category_parent_id

        else:

            markup = markups.categories(parent_id=int(text),
                                        chat_id=chat_id)

        if text.isdigit() and len(markup.keyboard) > 1:
            # если у категории есть подкатегории, то выводим их

            session.set(chat_id=chat_id,
                        key='category_parent_id',
                        value=int(text))

            text = Tx.get(chat_id=chat_id, text_id="BotMessages.AddPost.GET_CATEGORY")
            text = text[:14] + '<u>под</u>' + text[14:]

            bot.edit_message_text(chat_id=chat_id,
                                  text=text,
                                  message_id=message_id,
                                  reply_markup=markup)

        else:
            # если у категории нет дочерних категорий, то переходим в след. этап

            delete_message(chat_id=chat_id,
                           message_id=message_id)

            if not text.isdigit():
                text = category_parent_id

            session.set(chat_id=chat_id,
                        key='category_id',
                        value=int(text))

            pre_status(chat_id=chat_id)


def pre_status(chat_id: int):

    category_id = session.get(chat_id=chat_id,
                              key='category_id')

    if db_util.exists_status(category_id=category_id):
        get_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='search_status',
                    value=True)
        pre_buy_status(chat_id=chat_id)


def get_status(chat_id: int):

    send_message(chat_id=chat_id,
                 text_id="What status",
                 reply_markup=markups.get_status_product(chat_id=chat_id, search=True),
                 method=set_status)


@get_message_info
def set_status(chat_id, text, message_id):

    if text == Tx.get(chat_id=chat_id, text_id='Button.New'):
        status = True
    elif text == Tx.get(chat_id=chat_id, text_id='Button.Old'):
        status = False
    else:
        status = None

    session.set(chat_id=chat_id,
                key='search_status',
                value=status)

    pre_buy_status(chat_id=chat_id)


def pre_buy_status(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='category_id')

    if db_util.exists_buy_status(category_id=category_id):
        get_buy_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='search_buy_status',
                    value=False)
        start_search(chat_id=chat_id)


def get_buy_status(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='category_id')

    markup = markups.get_buy_status(chat_id=chat_id,
                                    back_=db_util.exists_buy_status(category_id=category_id))

    send_message(chat_id=chat_id,
                 text_id="What status",
                 reply_markup=markup,
                 method=set_buy_status)


@get_message_info
def set_buy_status(chat_id, text, message_id):

    if text == Tx.get(chat_id=chat_id, text_id='Buy'):
        status = True
    else:
        status = False

    session.set(chat_id=chat_id,
                key='search_buy_status',
                value=status)

    start_search(chat_id=chat_id)


def start_search(chat_id: int):

    category_id = session.get(chat_id=chat_id,
                              key='category_id')

    if posts := db_util.get_post_by_category_and_status(category_id=category_id,
                                                        chat_id=chat_id)[::-1]:
        get_next_direction_on_search(chat_id=chat_id,
                                     post=posts[0])

    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.PostCheck.NOT_POST_IN_CATEGORY",
                     reply_markup=markups.see_posts(chat_id=chat_id),
                     method=search_new_posts)


def get_next_direction_on_search(chat_id: int,
                                 post: Post):
    """
        По одному посту вычисляем дальнейшее местонахождение
        и если нужно переходы на некст страницу и обратно
    """
    next_id, prev_id, posts = db_util.get_left_and_right_post_id(category_id=post.category_id,
                                                                 post_id=post.id,
                                                                 chat_id=chat_id)
    session.set_next_and_prev_ids(chat_id=chat_id,
                                  next=next_id,
                                  prev=prev_id)

    if len(posts) > db_util.Constants.AMOUNT_POSTS_TO_CUS:
        text_id = "BotMessages.PostCheck.CLICK_ON_BUTTON_FOR_SEARCH"

    else:
        text_id = "BotMessages.PostCheck.SEARCH_LESS_THEN_LIMIT_POSTS"

    control_text = Tx.get(chat_id=chat_id, text_id=text_id)

    output_posts(to_chat_id=chat_id,
                 posts=posts,
                 user_status=db_util.Constants.STATUSES[0])

    send_message(chat_id=chat_id,
                 text=control_text,
                 reply_markup=markups.see_posts(next_id, prev_id, chat_id=chat_id),
                 method=search_new_posts)


@get_message_info
def search_new_posts(chat_id, text, *args):
    text = Tx.get_code_from_text(text)

    if text == "CheckCategories":
        send_message(chat_id=chat_id,
                     text_id="BotMessages.PostCheck.INPUT_NEED_CATEGORY",
                     reply_markup=markups
                     .categories(chat_id=chat_id,
                                 parent_id=session.get(chat_id=chat_id,
                                                       key='category_parent_id')))

    elif text == "Buttons.MAIN_MENU":
        start_bot(chat_id=chat_id)

    elif text in ("Buttons.Direction.RIGHT", "Buttons.Direction.LEFT"):

        category_id = session.get(chat_id=chat_id,
                                  key='category_id')

        post_index = session.get(chat_id=chat_id,
                                 key='next' if text == "Buttons.Direction.RIGHT" else 'prev')
        posts = db_util.get_post_by_category_and_status(category_id=category_id,
                                                        chat_id=chat_id)[::-1]
        get_next_direction_on_search(chat_id=chat_id,
                                     post=posts[post_index])

    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.AddPost.ERROR_PRODUCT_STATUS",
                     method=search_new_posts)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.GetGeo))
@get_message_info(callback=Callbacks.GetGeo)
def print_location(chat_id, text, message_id):
    long, lati = text.split('|')
    bot.send_location(chat_id=chat_id,
                      longitude=long,
                      latitude=lati)
