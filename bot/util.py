from typing import Union
from telebot import TeleBot
from telebot.types import BotCommand, CallbackQuery, Message, BotCommandScope
from bot.config import *
from bot import markups
from bot.validators import Validator, logger
import database.util as db_util
import datetime
import database.services.posts as db_util_post
from database.services.multitexting import Text as Tx
from database.services.session import SessionWork as session
import daemon_support.temp_storage as tmp_str
from functools import partial
import functools


bot = TeleBot(token=Constants.Telegram.TOKEN,
              parse_mode='html')


bot.set_my_commands([BotCommand(command, description) for command, description in COMMAND_DESCRIPTIONS.items()],
                    language_code='ru')
bot.set_my_commands([BotCommand(command, description) for command, description in COMMAND_DESCRIPTIONS_ON_UZB.items()],
                    language_code='uz')


def start_bot_from_code():
    logger.info('Bot Started')
    bot.remove_webhook()
    bot.infinity_polling()


def get_info_from_message(message: Union[Message, CallbackQuery], callback_str: str = None) -> tuple[int, str, int]:
    """
        Метод для получения данных с сообщения будь-то колбека или обычного
    :param callback_str: коллбек начало которое нужно обрезать
    :param message: необходимое сообщение
    :return: айди, текст, айди сообщения
    """
    tmp_str.new_user(chat_id=message.from_user.id)
    if isinstance(message, Message):
        if message.content_type != 'text':
            return message.from_user.id, message.caption, message.message_id
        else:
            return message.from_user.id, message.text, message.message_id
    else:
        return message.from_user.id, message.data[len(callback_str) - 2:], message.message.message_id


def schedule_message(chat_id: int, text: str, method, reply_markup=None):
    """
        Метод для регистрации следующего шага, чтоб писать меньше строк
    :param reply_markup:
    :param chat_id: кому отправлять
    :param text:    текст сообщения
    :param method:  нужный метод
    :param markup:  нужная клавиатура
    :return:
    """
    try:
        msg = bot.send_message(chat_id=chat_id,
                               text=text,
                               reply_markup=reply_markup,
                               parse_mode='html')
    except Exception as e:      # если бота заблокировали
        logger.error(f'Не удалось отправить сообщение с регистрацией шага из-за ошибки \n {e}')
    else:
        bot.register_next_step_handler(msg, method)
        return msg


def delete_message(message: Union[Message, CallbackQuery] = None,
                   chat_id: int = None,
                   message_id: int = None):
    """
        Удаление сообщения из канала с отловом эксепшина
    :param message: сообщение из которого получаются chat_id и message_id
    :param chat_id:
    :param message_id:
    :return:
    """
    try:
        if message:
            bot.delete_message(chat_id=message.chat.id if isinstance(message, Message) else message.from_user.id,
                               message_id=message.message_id if isinstance(message, Message) else message.message.message_id)
        else:
            bot.delete_message(chat_id=chat_id,
                               message_id=message_id)
    except Exception as e:
        logger.error(f'Не удалось удалить сообщение из-за ошибки \n {e}')


def send_message(chat_id: int,
                 text: str = None,
                 text_id: str = None,
                 reply_markup: Union[markups.ReplyKeyboardMarkup,
                                     markups.InlineKeyboardMarkup,
                                     markups.ReplyKeyboardRemove] = None,
                 method=None):

    if text_id:
        text = Tx.get(chat_id=chat_id,
                      text_id=text_id)

    try:
        if method:
            schedule_message(chat_id=chat_id,
                             text=text,
                             reply_markup=reply_markup,
                             method=method)

        else:
            bot.send_message(chat_id=chat_id,
                             text=text,
                             reply_markup=reply_markup)

    except Exception as e:
        logger.exception('Error in sending message')


def get_message_info(function=None, callback: str = ''):
    """
        Декоратор для получения сразу chat_id и текста или данных с сообщения
    """
    if function is None:
        return functools.partial(get_message_info, callback=callback)

    @functools.wraps(function)
    def wrapper(*args, **kwargs):

        if chat_id := kwargs.get('chat_id'):
            return_params = (chat_id,)

        else:
            message = args[0] if args else kwargs['message']
            return_params = get_info_from_message(message=message, callback_str=callback)

        return function(*return_params)

    return wrapper


def message_data_handler(code: str, message: Union[Message, CallbackQuery]) -> bool:
    """
        Обработка "ловли" сообщения на код если это хендлер на сообщение,
        или если это колбек на кнопке
    """
    if isinstance(message, Message):
        return code == Tx.get_code_from_text(message.text)

    else:
        return message.data.startswith(code[:code.find('_') + 1] if '_' in code else code)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.BackToStart))
@bot.message_handler(commands=Commands.START)
@bot.message_handler(func=partial(message_data_handler, "Buttons.MAIN_MENU"))
def start_bot(message: Message = None, chat_id: int = None):

    bot.clear_step_handler_by_chat_id(chat_id=chat_id)

    if message:

        if isinstance(message, CallbackQuery):
            chat_id, text, message_id = get_info_from_message(message=message, callback_str=message.data)
            delete_message(message)

        else:
            chat_id, text, message_id = get_info_from_message(message=message)

        logger.debug(f'User {chat_id} with @{message.from_user.username} start the bot')

    if not Validator.exist_user(chat_id=chat_id):
        # переходим в ветку регистрации

        from bot.services.registration import register_after_start
        register_after_start(chat_id=chat_id,
                             language_code=message.from_user.language_code)

    else:
        text = Tx.get(chat_id=chat_id,
                      text_id='BotMessages.MAIN_MENU')\
            .format(tmp_str.get_amount_players())

        user_status = db_util.get_user_status(chat_id=chat_id)

        if user_status == db_util.Constants.STATUSES[2]:
            text += Tx.get(chat_id=chat_id,
                           text_id='BotMessages.Blocked.ADD_IN_MAIN_MENU')\
                .format(db_util.get_expire_date(user_id=chat_id))

        elif user_status in db_util.Constants.STATUSES[3:]:
            text += '\n' + \
                Tx.get(chat_id=chat_id, text_id='amount_users_in_bot').format(db_util.UserWork.get_all_amount())

        session.set(chat_id=chat_id,
                    key='add_post',
                    value=False)
        send_message(chat_id=chat_id,
                     text=text,
                     reply_markup=markups.main_menu(chat_id=chat_id))


def edit_callback_message(chat_id: int,
                          message_id: int,
                          reply_markup: Union[markups.ReplyKeyboardMarkup, markups.InlineKeyboardMarkup] = None,
                          text: str = None,
                          text_id: str = None):
    """
        Метод для уменьшения кол-ва строк на изменение колбек сообщения с инлайн кнопками
    """
    if text or text_id:
        bot.edit_message_text(text=Tx.get(chat_id=chat_id, text_id=text_id) if text_id else text,
                              chat_id=chat_id,
                              message_id=message_id,
                              reply_markup=reply_markup)
    else:
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=reply_markup)


@bot.message_handler(commands=Commands.HELP)
def help_command(message: Message):
    chat_id = message.chat.id

    send_message(chat_id=chat_id,
                 text=Tx.get(
                     chat_id=chat_id,
                     text_id='BotMessages.HELP'
                 ))
