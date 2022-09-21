import time
from telebot.types import CallbackQuery
from database.services.multitexting import Text as Tx
from database.services.session import SessionWork as session
from bot import markups
from bot.config import Callbacks
from bot.util import bot, Message, Commands, get_info_from_message, schedule_message, delete_message, send_message
import database.util as db_util
from bot.services.output_posts import get_moderation_posts, send_all_new_posts_to_channel, send_new_post_to_channel
from bot.general_controllers import start_bot, logger


@bot.message_handler(func=lambda message: (message.text.endswith(
    Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.Moderator.NEW")[4:]) or
                                           message.text == '/' + Commands.MODERATE[0]) and
                                          db_util.get_user_status(chat_id=message.from_user.id) in
                                          db_util.Constants.STATUSES[3:])
def moderate_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} start moderation')
    if db_util.get_moderation_posts():
        get_moderation_posts(chat_id=chat_id)
    else:
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.Moderator.NO_MODERATION_POST'),
                         reply_markup=markups.main_menu(chat_id=chat_id))


def get_post_edit_menu(chat_id: int):
    """
        Метод для вывода меню и отловки след. сообщения для работы с объявлением
    :param chat_id: кому выводить
    :return:
    """
    schedule_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.PostCheck.EDIT_POST'),
                     reply_markup=markups.post_edit(chat_id=chat_id),
                     method=edit_post)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.MODERATE_POST[:-2]))
def get_moderation_post(callback: CallbackQuery):
    """
        Установка изменяемого обхявления и вывод меню на изменение его
    :param callback:
    :return:
    """
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.MODERATE_POST)

    delete_message(chat_id=chat_id,
                   message_id=message_id)

    if text == 'back':
        start_bot(message=callback)

    elif text.isdigit():
        session.set(chat_id=chat_id,
                    key='edit_post',
                    value=text)
        get_post_edit_menu(chat_id=chat_id)

    else:
        send_all_new_posts_to_channel()
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.ALL_POSTED'),
                         reply_markup=markups.main_menu(chat_id=chat_id))
        for post in db_util.get_moderation_posts():
            owner_id, post_title = db_util.activate_post(post_id=post.id)
            try:
                bot.send_message(chat_id=owner_id,
                                 text=Tx.get(chat_id=chat_id,
                                             text_id='BotMessages.PostCheck.POST_SUCCESS_POSTED_FOR_USUAL')
                                 .format(post_title))
            except Exception as e:
                logger.error(f'User {owner_id} block the bot. Error - {e}')
            time.sleep(.3)


def edit_post(message: Message):
    """
        Обработка меню изменения поста
    :param message:
    :return:
    """
    chat_id, text, message_id = get_info_from_message(message=message)
    post_id = session.get(chat_id=chat_id,
                          key='edit_post')

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.GO_TO_EDIT'),
                         reply_markup=markups.get_moderation_posts(chat_id=chat_id))

    elif text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.POST"):
        owner_id, post_title = db_util.activate_post(post_id=post_id)
        bot.send_message(chat_id=owner_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.POST_SUCCESS_POSTED_FOR_USUAL').format(post_title))
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.POST_SUCCESS_POSTED_FOR_MODERATOR').format(
                             post_title) +
                              '\n' +
                              Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.GO_TO_EDIT'),
                         reply_markup=markups.get_moderation_posts(chat_id=chat_id))
        send_new_post_to_channel(post_id=post_id)

    elif text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.DELETE"):
        schedule_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id,
                                     text_id='BotMessages.PostCheck.DELETE_POST_GET_CAUSE'),
                         method=delete_post,
                         reply_markup=markups.back(chat_id=chat_id))

    elif text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.EDIT_AND_POST"):
        what_change_in_post_schedule(chat_id=chat_id)


def delete_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} delete post')
    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_post_edit_menu(chat_id=chat_id)

    else:
        post_id = session.get(chat_id=chat_id,
                              key='edit_post')
        owner_id, post_title = db_util.delete_post(post_id=post_id,
                                                   cause=text)

        text_for_usual = Tx.get(chat_id=chat_id, text_id='BotMessages.PostCheck.DELETE_POST_FOR_USUAL').format(
            post_title, text)

        moderate_posts(message=message)
        send_message(chat_id=owner_id,
                     text=text_for_usual)

        text_for_moder = Tx.get(chat_id=chat_id, text_id='BotMessages.PostCheck.DELETE_POST_FOR_MODERATOR').format(
            post_title, text) + \
                         '\n' + \
                         Tx.get(chat_id=chat_id,
                                text_id='BotMessages.PostCheck.GO_TO_EDIT')

        send_message(chat_id=chat_id,
                     text=text_for_moder,
                     reply_markup=markups.get_moderation_posts(chat_id=chat_id))


def what_change_in_post_schedule(chat_id: int,
                                 text: str = ''):
    if not text:
        text = Tx.get(chat_id=chat_id, text_id="BotMessages.PostCheck.WHAT_YOU_WANNA_CHANGE")

    send_message(chat_id=chat_id,
                 text=text,
                 method=what_change_in_post,
                 reply_markup=markups.what_edit_in_post(chat_id=chat_id))


def what_change_in_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} start change post')

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_post_edit_menu(chat_id=chat_id)

    elif text in (Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.TITLE"),
                  Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.DESCRIPTION"),
                  Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.PRICE")):

        if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.TITLE"):
            session.set(chat_id=chat_id, key='post_part_to_edit', value='title')
        elif text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.DESCRIPTION"):
            session.set(chat_id=chat_id, key='post_part_to_edit', value='description')
        elif text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.PostEdit.PRICE"):
            session.set(chat_id=chat_id, key='post_part_to_edit', value='price')

        send_message(chat_id=chat_id,
                     text_id='BotMessages.PostCheck.INPUT_NEW_VALUE',
                     method=change_part_of_post,
                     reply_markup=markups.back(chat_id=chat_id))

    else:
        what_change_in_post_schedule(chat_id=chat_id,
                                     text=Tx.get(chat_id=chat_id,
                                                 text_id='BotMessages.AddPost.ERROR_PRODUCT_STATUS'))


def change_part_of_post(message: Message):
    """
        Изменение описание поста
    :param message:
    :return:
    """
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} change post')
    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        what_change_in_post_schedule(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='post_part_new_value',
                    value=text)

        send_message(chat_id=chat_id,
                     text_id='BotMessages.PostCheck.CHANGE_POST_GET_CAUSE',
                     method=change_post,
                     reply_markup=markups.back(chat_id=chat_id))


def change_post(message: Message):
    """
        Изменение уже самого поста
    :param message:
    :return:
    """
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} end change post')

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        what_change_in_post_schedule(chat_id=chat_id)

    else:
        post_id = session.get(chat_id=chat_id,
                              key='edit_post')
        new_part_type = session.get(chat_id=chat_id,
                                    key='post_part_to_edit')
        new_part_value = session.get(chat_id=chat_id,
                                     key='post_part_new_value')
        owner_id, post_title = db_util.change_post(post_id=post_id,
                                                   cause=text,
                                                   **{new_part_type: new_part_value})

        russian_type = {'title': 'название',
                        'description': 'описание',
                        'price': 'цена'}

        send_message(chat_id=owner_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.PostCheck.CHANGE_POST_FOR_USUAL').format(post_title,
                                                                                               text,
                                                                                               russian_type.get(
                                                                                                   new_part_type),
                                                                                               new_part_value))

        text_for_moderator = '\n'.join((Tx.get(chat_id=chat_id, text_id='BotMessages.PostCheck'
                                                                        '.CHANGE_POST_FOR_MODERATOR').format(
            post_title, text),
                                        Tx.get(chat_id=chat_id,
                                               text_id='BotMessages.PostCheck.GO_TO_EDIT')))

        send_message(chat_id=chat_id,
                     text=text_for_moderator,
                     reply_markup=markups.get_moderation_posts(chat_id=chat_id))
