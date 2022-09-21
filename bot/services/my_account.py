from bot import markups
from bot.services.cities import get_city
from bot.util import bot, Message, Commands, get_info_from_message
import database.util as db_util
from database.services.multitexting import Text as Tx
from database.services.session import SessionWork as session
from project_configuration import logging


@bot.message_handler(
    func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.ACCOUNT") and
                         db_util.get_user_status(chat_id=message.from_user.id) != db_util.Constants.STATUSES[2])
@bot.message_handler(commands=Commands.PRIVATE_OFFICE)
@logging()
def my_account(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    msg = bot.send_message(chat_id=chat_id,
                           text=Tx.get(chat_id=chat_id,
                                       text_id="BotMessages.MyAccount.WELCOME"),
                           reply_markup=markups.my_account(chat_id=chat_id))


@bot.message_handler(func=lambda message: message
                     .text
                     .startswith(Tx.get(chat_id=message.from_user.id,
                                        text_id="Buttons.Account.CHANGE_CITY")[:-3]) and
                                          db_util.get_user_status(chat_id=message.from_user.id) !=
                                          db_util.Constants.STATUSES[2])
@logging()
def change_city(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    get_city(chat_id=chat_id)


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Account.ChangeLanguage") and
                                          db_util.get_user_status(chat_id=message.from_user.id) !=
                                          db_util.Constants.STATUSES[2])
@bot.message_handler(commands=Commands.LANGUAGE)
@logging()
def change_language(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    current_language_id = session.get(chat_id=chat_id,
                                      key='language')
    lang_id = 1 if not current_language_id or int(current_language_id) == 2 else 2
    session.set(chat_id=chat_id,
                key='language',
                value=lang_id)
    bot.send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id="BotMessages.MyAccount.ChangeLanguageSuccess"),
                     reply_markup=markups.my_account(chat_id=chat_id))
