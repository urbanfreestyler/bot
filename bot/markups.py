import database.util as db_util
from database.services.multitexting import Text as Tx
from database.services.patterns import PatternsWork, get_pattern_questions
from database.services.session import SessionWork as session
from telebot.types import ReplyKeyboardMarkup, ReplyKeyboardRemove, KeyboardButton, InlineKeyboardMarkup, \
    InlineKeyboardButton
from database.config import Constants as db_constants
from bot.config import Keyboards, Callbacks, Constants
from copy import deepcopy
from database.models import Users


def _reply_markup(chat_id: int,
                  keyboard: list = [],
                  back_: bool = False,
                  continue_: bool = False,
                  skip: bool = False,
                  one_time: bool = False,
                  main_menu_: bool = False) -> ReplyKeyboardMarkup:
    """
        Паттерн для DRY для replymarkup
    :param keyboard: нужная клавиатура
    :param back_: если нужно назад - истина
    :param continue_: если нужно продолжить - истина
    :param main_menu_: кнопка в главное меню
    :return:
    """
    markup = ReplyKeyboardMarkup(resize_keyboard=True,
                                 one_time_keyboard=one_time)

    if keyboard:
        for row in keyboard:
            button_row = [KeyboardButton(text=Tx.get(chat_id=chat_id, text_id=button_title)) for button_title in row]
            markup.add(*button_row)

    if continue_:
        markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.CONTINUE")))

    if skip:
        markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="skip")))

    if back_:
        markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK")))

    if main_menu_:
        markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.MAIN_MENU")))

    return markup


def _inline_markup(keyboard, callback_str: str) -> InlineKeyboardMarkup:
    """
        Паттерн для DRY для inlinemarkup
    :param keyboard: нужная клавиатура
    :return:
    """
    markup = InlineKeyboardMarkup()

    for row in keyboard:
        button_row = [InlineKeyboardButton(text=button_title,
                                           callback_data=callback_str.format(button_title)) for button_title in row]
        markup.add(*button_row)

    return markup


def get_phone(chat_id: int, back_: bool = False):
    markup = ReplyKeyboardMarkup(one_time_keyboard=True,
                                 resize_keyboard=True)

    markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id,
                                          text_id='Buttons.GET_PHONE'),
                              request_contact=True))

    if back_:
        markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id='Buttons.Direction.BACK')))

    return markup


def main_menu(chat_id: int) -> ReplyKeyboardMarkup:
    status = db_util.get_user_status(chat_id=chat_id)
    if status in db_constants.STATUSES[0:2]:
        keyboard = Keyboards.Menu.Main.USUAL

        markup = _reply_markup(keyboard=keyboard,
                               chat_id=chat_id)

    elif status == db_constants.STATUSES[2]:
        keyboard = Keyboards.Menu.Main.BLOCKED

        markup = _reply_markup(keyboard=keyboard,
                               chat_id=chat_id)

    else:
        if status == db_constants.STATUSES[3]:
            keyboard = deepcopy(Keyboards.Menu.Main.MODERATOR)
        else:
            keyboard = deepcopy(Keyboards.Menu.Main.ADMIN)

        markup = _reply_markup(keyboard=keyboard,
                               chat_id=chat_id)

        notification = markup.keyboard[0][0]['text']
        markup.keyboard[0][0]['text'] = notification[:3] + str(len(db_util.get_moderation_posts())) + notification[3:]

    return markup


def get_city_for_markup(chat_id: int):
    if chat_id:
        city = session.get(chat_id=chat_id,
                           key='search_city')
        city = None if city == 'all' else city
    else:
        city = None
    return city


def categories(offset: int = 0,
               parent_id: int = None,
               callback_data: str = Callbacks.CATEGORY,
               add_post: bool = False,
               chat_id: int = 0) -> InlineKeyboardMarkup:
    """
        Вывод категорий в виде клавиатуры
    :param chat_id: для поиска по городу (в сессии хранится город)
    :param add_post: если идёт добавление поста - не выводим кнопку все
    :param callback_data: для того, чтоб эту клавиатуру использовать как для поиска продукции,
                          так и для изменения категорий
    :param offset: сколько категорий пропустить  (для перелистывания)
    :param parent_id: айди родительской категории, просмотр есть ли у родителя дети
    :return: вывод категорий которые нашлись, если у родителя нет категорий - выводим None
    """
    city = get_city_for_markup(chat_id=chat_id)

    pattern_id = session.get(chat_id=chat_id,
                             key='pattern_id')

    _categories = db_util.get_categories(parent_id=parent_id,
                                         chat_id=chat_id,
                                         pattern_id=pattern_id)

    markup = InlineKeyboardMarkup(row_width=2)

    if _categories:
        # если у категории есть ещё подкатегории, иначе - выход
        amount_categories = len(_categories)

        if _categories[offset: offset + db_constants.LIMIT_CATEGORIES]:
            # чтоб при перелистывании не зашли за лимит
            prev_offset = offset - db_constants.LIMIT_CATEGORIES
            next_offset = offset + db_constants.LIMIT_CATEGORIES
            _categories = _categories[offset: offset + db_constants.LIMIT_CATEGORIES]

        else:
            prev_offset, next_offset = 0, db_constants.LIMIT_CATEGORIES
            _categories = _categories[prev_offset: next_offset]

        markup = InlineKeyboardMarkup(row_width=2)
        buttons = []

        if parent_id and callback_data == Callbacks.CATEGORY and not add_post:
            button_text = f'{Tx.get(chat_id=chat_id, text_id="Buttons.ALL")} '
            button_text += str(db_util.get_amount_posts_in_category(category_id=parent_id,
                                                                    city=city,
                                                                    ))
            markup.add(InlineKeyboardButton(text=button_text,
                                            callback_data=callback_data.format('all')), )

        for category_id, category_title in _categories:
            button_text = f'{category_title} '

            if not add_post:
                button_text += str(db_util.get_amount_posts_in_category(category_id=category_id,
                                                                        city=city,
                                                                        ))

            buttons.append(InlineKeyboardButton(text=button_text,
                                                callback_data=callback_data.format(category_id)))

        markup.add(*buttons)

        control_buttons = []

        if offset > 0:
            control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.LEFT"),
                                                        callback_data=callback_data.format(
                                                            Callbacks.Direction.LEFT + f'_{prev_offset}')))

        if amount_categories > next_offset:
            control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.RIGHT"),
                                                        callback_data=callback_data.format(
                                                            Callbacks.Direction.RIGHT + f'_{next_offset}')))

        markup.add(*control_buttons)

    markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=callback_data.format('back')))

    if callback_data != Callbacks.CATEGORY:
        # для админов
        admin_control_buttons = []
        for row in Keyboards.Menu.Admin.CATEGORIES_EDIT:
            row = deepcopy(row)
            row = row[-1:] if not parent_id else row
            for key in row:
                admin_control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id=key),
                                                                  callback_data=callback_data.format(key)))
        markup.add(*admin_control_buttons)

    return markup


def product_status_for_customer(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.SEARCH_PRODUCT_STATUS,
                         back_=True,
                         main_menu_=True,
                         chat_id=chat_id)


# def product_status(chat_id: int):
#     return _reply_markup(keyboard=Keyboards.Menu.AddPost.PRODUCT_STATUS,
#                          back_=True,
#                          chat_id=chat_id)


def back(chat_id: int, continue_: bool = False, skip: bool = False):
    return _reply_markup(back_=True,
                         continue_=continue_,
                         skip=skip,
                         chat_id=chat_id)


def preview(chat_id: int):
    return _reply_markup(keyboard=Keyboards.PREVIEW,
                         chat_id=chat_id)


def post_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.POSTS,
                         one_time=True,
                         chat_id=chat_id)


def balance_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.BALANCE,
                         one_time=True,
                         chat_id=chat_id)


def add_balance_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.ADD_BALANCE,
                         one_time=True,
                         chat_id=chat_id)


def add_sum(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.ADD_SUM,
                         one_time=True,
                         chat_id=chat_id)


def withdraw_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.WITHDRAW_BALANCE,
                         one_time=True,
                         chat_id=chat_id)


def my_card_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.MY_CARD,
                         one_time=True,
                         chat_id=chat_id)


def confirm_card_number(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.CARD_CONFIRMATION,
                         one_time=True,
                         chat_id=chat_id)


def add_card(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.ADD_CARD,
                         one_time=True,
                         chat_id=chat_id)


def partner_menu(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.PARTNERS,
                         one_time=True,
                         chat_id=chat_id)


def post_edit(chat_id: int):
    return _reply_markup(keyboard=Keyboards.Menu.EDIT_POST,
                         back_=True,
                         chat_id=chat_id)


def get_full_users_list(status: str, offset: int):
    _users = db_util.get_users_list(status=status)[:]
    amount_users = len(_users[offset + db_constants.LIMIT_USERS:])

    if _users[offset: offset + db_constants.LIMIT_USERS]:
        # чтоб при перелистывании не зашли за лимит
        prev_offset = offset - db_constants.LIMIT_USERS
        next_offset = offset + db_constants.LIMIT_USERS
        _users = _users[offset: offset + db_constants.LIMIT_USERS]

    else:
        prev_offset, next_offset = 0, db_constants.LIMIT_USERS
        _users = _users[prev_offset: next_offset]

    return _users, amount_users, prev_offset, next_offset


def get_full_posts_list(status: str, offset: int):
    _posts = db_util.get_posts_list(status=status)[:]
    amount_posts = len(_posts[offset + db_constants.LIMIT_POSTS:])

    if _posts[offset: offset + db_constants.LIMIT_POSTS]:
        # чтоб при перелистывании не зашли за лимит
        prev_offset = offset - db_constants.LIMIT_POSTS
        next_offset = offset + db_constants.LIMIT_POSTS
        _posts = _posts[offset: offset + db_constants.LIMIT_POSTS]

    else:
        prev_offset, next_offset = 0, db_constants.LIMIT_POSTS
        _posts = _posts[prev_offset: next_offset]

    return _posts, amount_posts, prev_offset, next_offset


def get_full_own_posts_list(chat_id: int, status: str, offset: int):
    _posts = db_util.get_own_posts_list(chat_id=chat_id, status=status)[:]
    amount_posts = len(_posts[offset + db_constants.LIMIT_POSTS:])

    if _posts[offset: offset + db_constants.LIMIT_POSTS]:
        # чтоб при перелистывании не зашли за лимит
        prev_offset = offset - db_constants.LIMIT_POSTS
        next_offset = offset + db_constants.LIMIT_POSTS
        _posts = _posts[offset: offset + db_constants.LIMIT_POSTS]

    else:
        prev_offset, next_offset = 0, db_constants.LIMIT_POSTS
        _posts = _posts[prev_offset: next_offset]

    return _posts, amount_posts, prev_offset, next_offset


def get_users_list_with_contains(contains: str):
    _users = db_util.get_users_list_with_nick(contains=contains)
    return _users, 0, 0, 0


def get_posts_list_with_contains(contains: str):
    _posts = db_util.get_posts_list_with_id(contains=contains)
    return _posts, 0, 0, 0


def get_own_posts_list_with_contains(contains: str, chat_id: int):
    _posts = db_util.get_own_posts_list_with_id(contains=contains, chat_id=chat_id)
    return _posts, 0, 0, 0


def users(chat_id: int,
          offset: int = 0,
          status: str = db_util.Constants.STATUSES[3],
          contains: str = ''
          ) -> InlineKeyboardMarkup:
    """
        Вывод пользователя в виде клавиатуры
    :param status: статус человека, админ или модер
    :param offset: сколько пользователей пропустить  (для перелистывания)
    :param contains: фильтр по пользователям
    :return: вывод категорий которые нашлись, если у родителя нет категорий - выводим None
    """
    status = db_util.get_user_status(chat_id=chat_id)

    if contains:
        _users, amount_users, prev_offset, next_offset = get_users_list_with_contains(contains)

    else:
        _users, amount_users, prev_offset, next_offset = get_full_users_list(status=status,
                                                                             offset=offset)

    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []

    for user_id, user_username, user_first_name, user_status in _users:
        picture = Constants.Telegram.STATUSES_PICTURES.get(user_status)
        text = picture + ' ' + (f'@{user_username}' if user_username else user_first_name)
        buttons.append(InlineKeyboardButton(text=text,
                                            callback_data=Callbacks
                                            .USERS_CHANGER
                                            .format(status + '_' + str(user_id))))

    markup.add(*buttons)

    control_buttons = []

    if offset != 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.LEFT"),
                                                    callback_data=Callbacks.USERS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.LEFT + f'__{prev_offset}')))

    control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                            text_id="Buttons.Direction.BACK"),
                                                callback_data=Callbacks.USERS_CHANGER.format('_back')))

    if amount_users > 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.RIGHT"),
                                                    callback_data=Callbacks.USERS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.RIGHT + f'__{next_offset}')))

    markup.add(*control_buttons)

    return markup


def posts(chat_id: int,
          offset: int = 0,
          status: str = db_util.Constants.STATUSES[3],
          contains: str = ''
          ) -> InlineKeyboardMarkup:
    """
        Вывод постов в виде клавиатуры
    :param status: статус человека, админ или модер
    :param offset: сколько пользователей пропустить  (для перелистывания)
    :param contains: фильтр по пользователям
    :return: вывод категорий которые нашлись, если у родителя нет категорий - выводим None
    """
    status = db_util.get_user_status(chat_id=chat_id)

    if contains:
        _posts, amount_posts, prev_offset, next_offset = get_posts_list_with_contains(contains)

    else:
        _posts, amount_posts, prev_offset, next_offset = get_full_posts_list(status=status,
                                                                             offset=offset)

    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []

    for post_id, post_owner_id, post_city in _posts:
        text = (f'{post_id}' if post_id else post_owner_id)
        buttons.append(InlineKeyboardButton(text=text,
                                            callback_data=Callbacks
                                            .POSTS_CHANGER
                                            .format(status + '_' + str(post_id))))

    markup.add(*buttons)

    control_buttons = []

    if offset != 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.LEFT"),
                                                    callback_data=Callbacks.POSTS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.LEFT + f'__{prev_offset}')))

    control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                            text_id="Buttons.Direction.BACK"),
                                                callback_data=Callbacks.POSTS_CHANGER.format('_back')))

    if amount_posts > 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.RIGHT"),
                                                    callback_data=Callbacks.POSTS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.RIGHT + f'__{next_offset}')))

    markup.add(*control_buttons)

    return markup


def reactions_to_post(counter: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    reactions = db_util.Reaction.select()

    buttons = []

    for reaction in reactions:
        buttons.append(InlineKeyboardButton(text=reaction.text + ' ' + str(counter) if counter else reaction.text,
                                            callback_data=reaction.text))

    markup.add(*buttons)
    return markup


def own_posts(chat_id: int,
              offset: int = 0,
              status: str = db_util.Constants.STATUSES[3],
              contains: str = '',
              owner_id: int = ''
              ) -> InlineKeyboardMarkup:
    """
        Вывод постов в виде клавиатуры
    :param status: статус человека, админ или модер
    :param offset: сколько пользователей пропустить  (для перелистывания)
    :param contains: фильтр по пользователям
    :return: вывод категорий которые нашлись, если у родителя нет категорий - выводим None
    """

    status = db_util.get_user_status(chat_id=chat_id)
    # if owner_id:
    # _posts, amount_posts, prev_offset, next_offset = get_own_posts_list_with_contains(owner_id=chat_id)

    if contains:
        _posts, amount_posts, prev_offset, next_offset = get_own_posts_list_with_contains(contains=contains,
                                                                                      chat_id=chat_id)
    else:
        _posts, amount_posts, prev_offset, next_offset = get_full_own_posts_list(chat_id=chat_id,
                                                                                 status=status,
                                                                                 offset=offset)

    markup = InlineKeyboardMarkup(row_width=3)
    buttons = []

    for post_id, post_owner_id, post_city in _posts:
        text = (f'{post_id}' if post_id else post_owner_id)
        buttons.append(InlineKeyboardButton(text=text,
                                            callback_data=Callbacks
                                            .OWN_POSTS_CHANGER
                                            .format(status + '_' + str(post_id))))

    markup.add(*buttons)

    control_buttons = []

    if offset != 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.LEFT"),
                                                    callback_data=Callbacks.OWN_POSTS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.LEFT + f'__{prev_offset}')))

    control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                            text_id="Buttons.Direction.BACK"),
                                                callback_data=Callbacks.OWN_POSTS_CHANGER.format('_back')))

    if amount_posts > 0:
        control_buttons.append(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
                                                                text_id="Buttons.Direction.RIGHT"),
                                                    callback_data=Callbacks.OWN_POSTS_CHANGER.format(
                                                        status + '_' + Callbacks.Direction.RIGHT + f'__{next_offset}')))

    markup.add(*control_buttons)

    return markup


def send_post_to_customer(chat_id: int, current_post_id: str = '-1') -> InlineKeyboardMarkup:
    category_id = session.get(chat_id=chat_id,
                              key='category_id')
    posts = db_util.get_post_by_category_and_status(category_id=category_id,
                                                    chat_id=chat_id)[::-1]
    posts_ids = tuple(post.id for post in posts)

    if current_post_id == '-1':
        post_id = posts_ids[0]
    else:
        post_id = int(current_post_id)

    markup = InlineKeyboardMarkup(row_width=3)

    left_callback = Callbacks \
        .SEARCH_POSTS \
        .format(posts_ids[posts_ids.index(post_id) - 1]) if posts_ids.index(post_id) > 0 else ''

    right_callback = Callbacks \
        .SEARCH_POSTS \
        .format(posts_ids[posts_ids.index(post_id) + 1]) if posts_ids.index(post_id) < len(posts_ids) - 1 else ''

    buttons = [InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=Callbacks.SEARCH_POSTS.format('back'))]

    if left_callback:
        buttons = [InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.LEFT"),
                                        callback_data=left_callback), ] + buttons
    if right_callback:
        buttons += [InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.RIGHT"),
                                         callback_data=right_callback), ]

    markup.add(*buttons)

    return markup


def user_edit_menu(status: str, user_id: str) -> InlineKeyboardMarkup:
    """
        Меню для работы с юзером для модера, админа, и главного админа
    :param status: статус того, кто зашел
    :param user_id: айди обрабатываемого человека
    :return:
    """

    markup = InlineKeyboardMarkup(row_width=2)

    if status == db_util.Constants.STATUSES[3]:
        keyboard = deepcopy(Keyboards.Menu.Moderator.USER_EDIT)
    elif status == db_util.Constants.STATUSES[4]:
        keyboard = deepcopy(Keyboards.Menu.Admin.USER_EDIT)
    else:
        keyboard = deepcopy(Keyboards.Menu.MainAdmin.USER_EDIT)

    markup.add(*(InlineKeyboardButton(text=Tx.get(chat_id=int(user_id), text_id=key),
                                      callback_data=Callbacks.USER_EDIT.format(
                                          Tx.get(chat_id=int(user_id), text_id=key) + '__' + user_id)) for row in
                 keyboard
                 for key in row))

    return markup


def post_edit_menu(status: str, user_id: str) -> InlineKeyboardMarkup:
    """
        Меню для работы с постом для модера, админа, и главного админа
    :param status: статус того, кто зашел
    :param user_id: айди обрабатываемого человека
    :return:
    """

    markup = InlineKeyboardMarkup(row_width=2)
    if status == db_util.Constants.STATUSES[3]:
        keyboard = deepcopy(Keyboards.Menu.Moderator.POST_DELETE)
    elif status == db_util.Constants.STATUSES[4]:
        keyboard = deepcopy(Keyboards.Menu.Admin.POST_DELETE)
    else:
        keyboard = deepcopy(Keyboards.Menu.MainAdmin.POST_DELETE)
    markup.add(*(InlineKeyboardButton(text=Tx.get(chat_id=int(user_id), text_id=key),
                                      callback_data=Callbacks.POST_DELETE.format(
                                          Tx.get(chat_id=int(user_id), text_id=key) + '__' + user_id)) for row in
                 keyboard
                 for key in row))

    return markup


def own_post_edit_menu(status: str, user_id: str) -> InlineKeyboardMarkup:
    """
        Меню для работы с постом для модера, админа, и главного админа
    :param status: статус того, кто зашел
    :param user_id: айди обрабатываемого человека
    :return:
    """

    markup = InlineKeyboardMarkup(row_width=2)
    keyboard = deepcopy(Keyboards.Menu.OWN_POST_DELETE)
    markup.add(*(InlineKeyboardButton(text=Tx.get(chat_id=int(user_id), text_id=key),
                                      callback_data=Callbacks.OWN_POST_DELETE.format(
                                          Tx.get(chat_id=int(user_id), text_id=key) + '__' + user_id)) for row in
                 keyboard
                 for key in row))

    return markup


def edit_category(chat_id: int):
    return _reply_markup(back_=True,
                         keyboard=Keyboards.Menu.Admin.CATEGORIES_EDIT,
                         chat_id=chat_id)


def yes_or_not(chat_id: int, back_: bool = True):
    return _reply_markup(keyboard=Keyboards.YES_OR_NOT,
                         back_=back_,
                         chat_id=chat_id)


def clear_markup():
    return ReplyKeyboardRemove()


def settings(chat_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    for setting in db_util.get_settings_list():
        markup.add(InlineKeyboardButton(text=f'{setting.title} - {setting.value} {setting.endings}',
                                        callback_data=Callbacks.SETTINGS.format(setting.id)))

    markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=Callbacks.SETTINGS.format('back')))
    return markup


def see_posts(next: int = -1, prev: int = -1, chat_id: int = 0) -> ReplyKeyboardMarkup:
    keyboard = [[]]

    if prev != -1:
        keyboard[0].append("Buttons.Direction.LEFT")

    if next != -1:
        keyboard[0].append("Buttons.Direction.RIGHT")

    keyboard.append([["CheckCategories"]])

    return _reply_markup(keyboard=keyboard,
                         # back_=True,
                         main_menu_=True,
                         chat_id=chat_id)


def get_cities(callback: str) -> InlineKeyboardMarkup:
    """
        Вывод городов в кнопках для регистрации / изменения города
    """
    markup = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for city in db_util.get_cities():
        buttons.append(InlineKeyboardButton(text=city.title,
                                            callback_data=callback.format(city.id)))
    markup.add(*buttons)
    return markup


def get_city_for_search(chat_id: int, back_: bool = False) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    callback, buttons = Callbacks.SEARCH_CITY, []
    categories = db_util.get_categories_ids_by_pattern_id(pattern_id=session.get(chat_id=chat_id,
                                                                                 key='pattern_id'))
    categories = tuple(cat[0] for cat in categories)

    for city in db_util.get_cities():
        buttons.append(InlineKeyboardButton(text=city.title + db_util.get_post_amount_from_city_id(city_id=city.id,
                                                                                                   categories=categories),
                                            callback_data=callback.format(city.id)))

    markup.add(*buttons)
    markup.add(InlineKeyboardButton(text=Tx
                                    .get(chat_id=chat_id, text_id="Buttons.SearchCity.ALL_CITY")
                                    .format(db_util.get_post_amount_from_city_id(categories=categories)),
                                    callback_data=callback.format('all')))

    if back_:
        markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                        callback_data=callback.format('back')))
    return markup


def my_account(chat_id: int) -> ReplyKeyboardMarkup:
    keyboard = deepcopy(Keyboards.Menu.ACCOUNT)
    markup = _reply_markup(keyboard=keyboard, chat_id=chat_id)
    city = db_util.get_user_data(user_id=str(chat_id)).city
    markup.keyboard[0][1]['text'] = markup.keyboard[0][1]['text'] \
        .format(city.title if city else None)
    return markup


def get_moderation_posts(chat_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=4)
    buttons = []
    for post in db_util.get_moderation_posts():
        buttons.append(InlineKeyboardButton(text=post.id,
                                            callback_data=Callbacks.MODERATE_POST.format(post.id)))
    markup.add(*buttons)
    markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=Callbacks.MODERATE_POST.format('back')),
               InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.POST_ALL"),
                                    callback_data=Callbacks.MODERATE_POST.format('all')))
    return markup


def what_edit_in_post(chat_id: int) -> ReplyKeyboardMarkup:
    return _reply_markup(keyboard=Keyboards.Menu.EDIT_POST_PART,
                         back_=True,
                         chat_id=chat_id)


def start_language_menu(chat_id: int) -> ReplyKeyboardMarkup:
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.Menu.Language)





# def get_current_geo(chat_id: int, skip: bool = False):
#     """
#         Метод на получение текущего гео ,
#         (при установке обновления)
#     """
#     markup = ReplyKeyboardMarkup(resize_keyboard=True)
#     markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id,
#                                           text_id='Buttons.GetCurrentGeo'),
#                               request_location=True))
#
#     if skip:
#         markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="skip")))
#
#     markup.add(KeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK")))
#
#     return markup


# def get_geo(chat_id: int, post_id: int = None, long=None, lati=None) -> InlineKeyboardMarkup:
#     """
#         Метод при ПРОСМОТРЕ И ПОИСКЕ
#     """
#     if post_id:
#         long, lati = db_util.get_location(str(post_id))
#     markup = InlineKeyboardMarkup()
#     markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id,
#                                                 text_id='Buttons.GetGeo'),
#                                     callback_data=Callbacks.GetGeo.format(f'{long}|{lati}')))
#     return markup


def get_texts_from_db(text: str) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)
    for bot_message in db_util.get_texts(text=text):
        markup.add(InlineKeyboardButton(text=bot_message.text,
                                        callback_data=Callbacks.ChangeText.format(bot_message.id)))
    return markup


def get_search_types(chat_id: int) -> ReplyKeyboardMarkup:
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.SearchTypes,
                         main_menu_=True)


def patterns(chat_id: int,
             admin: bool = False,
             edit_categories: bool = False,
             search: bool = False,
             change_answer: bool = False) -> InlineKeyboardMarkup:
    """
        Генерации клавиатуры паттерна
        admin: если админ, другие калбеки
        edit_categories: если изменяем категорию
        search: если поиск - true,
        по умолчанию сделано для создания поста
        change_answer - смена длины ответа
    """
    markup = InlineKeyboardMarkup()
    buttons = []

    if admin:
        callback = Callbacks.AdminPattern
    elif edit_categories:
        callback = Callbacks.PatternEditCategories
    elif search:
        callback = Callbacks.PatternSearchPost
    elif change_answer:
        callback = Callbacks.PatternEditAnswer
    else:
        callback = Callbacks.Pattern

    for pattern_id, pattern_title in PatternsWork.get_patterns(chat_id=chat_id):
        buttons.append(InlineKeyboardButton(text=pattern_title,
                                            callback_data=callback.format(pattern_id)))

    markup.add(*buttons)

    if not admin:
        markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                        callback_data=callback.format('back')))

    return markup


def manipulate_patterns(chat_id: int) -> InlineKeyboardMarkup:
    patterns_keyboard = patterns(chat_id=chat_id,
                                 admin=True)

    patterns_keyboard.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id='Buttons.Direction.BACK'),
                                               callback_data=Callbacks.BackToStart),
                          InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id='Button.Patterns.Create'),
                                               callback_data=Callbacks.PatternAdd))
    return patterns_keyboard


def channels(chat_id: int, pattern_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=1)

    p_id = db_util.PatternsMultiLang.get(pattern_id=pattern_id)
    channels_for_post = db_util.Channel.filter(pattern_id=p_id)
    for channel in channels_for_post:
        markup.add(InlineKeyboardButton(chat_id=chat_id, text=channel.name + " — " +
                                                              str(channel.price_for_post) + ' сум'
        if not channel.price_for_post == 0 else channel.name + " — " + 'Бесплатно',
                                        callback_data=str(channel.id)))

    markup.add(InlineKeyboardButton(chat_id=chat_id, text=Tx.get(chat_id=chat_id,
                                                                 text_id="Buttons.Continue"),
                                    callback_data=Callbacks.Continue))

    return markup


def payment(chat_id: int) -> ReplyKeyboardMarkup:
    return _reply_markup(keyboard=Keyboards.Menu.PAYMENT,
                         chat_id=chat_id,
                         back_=True)


def change_pattern(chat_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=Callbacks.BackToStart),
               InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id='Button.Patterns.Change'),
                                    callback_data=Callbacks.PatternChange),
               InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id='Button.Patterns.Remove'),
                                    callback_data=Callbacks.PatternRemove))
    return markup


def get_questions_to_edit_answer(pattern_id: str, chat_id: int):
    markup = InlineKeyboardMarkup()
    callback = Callbacks.QuestionToEdit

    for question in get_pattern_questions(pattern_id=pattern_id,
                                          chat_id=chat_id):
        if question[1].startswith('photo') or question[1].startswith('text') or question[1].startswith('int'):
            markup.add(InlineKeyboardButton(text=question[2],
                                            callback_data=callback.format(question[0])))

    markup.add(InlineKeyboardButton(text=Tx.get(chat_id=chat_id, text_id="Buttons.Direction.BACK"),
                                    callback_data=callback.format('back')))
    return markup


def to_main_menu(chat_id: int):
    return _reply_markup(chat_id=chat_id,
                         keyboard=[["Buttons.MAIN_MENU"]])


def set_question_about_status(chat_id: int):
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.SetStatus,
                         back_=True)


def get_status_product(chat_id: int, search: bool = False, back_: bool = True):
    keyboard = Keyboards.GetStatus[:]
    if search:
        keyboard.insert(0, ['Buttons.ProductStatus.ALL'])
    return _reply_markup(chat_id=chat_id,
                         keyboard=keyboard,
                         back_=back_)


def get_currencies(chat_id: int):
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.Currencies,
                         # back_=True
                         )


def get_reedit_post_menu(chat_id: int):
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.ReEditPost)


def get_buy_status(chat_id: int, back_: bool = False):
    return _reply_markup(chat_id=chat_id,
                         keyboard=Keyboards.BuyStatus,
                         back_=back_)


def skip_keyboard(chat_id: int, back_: bool = False):
    return _reply_markup(chat_id=chat_id,
                         skip=True,
                         back_=back_)
