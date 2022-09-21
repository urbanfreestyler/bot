from bot.general_controllers import start_bot
from bot.util import *
from project_configuration import logging


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Admin.SETTINGS") and
                                          db_util.get_user_status(chat_id=message.from_user.id) in
                                          db_util.Constants.STATUSES[4:])
@logging()
def manipulate_with_settings(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} use {text}')
    bot.send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id, text_id="BotMessages.Setting.LIST"),
                     reply_markup=markups.settings(chat_id=chat_id))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.SETTINGS[:-2]))
def setup_setting(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.SETTINGS)
    if text == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        start_bot(message=callback)

    else:
        session.set(chat_id=chat_id,
                    key='setting_id',
                    value=text)
        get_setting_value(chat_id=chat_id)


def get_setting_value(chat_id: int):
    schedule_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id, text_id="BotMessages.Setting.INPUT_NEW_VALUE"),
                     reply_markup=markups.back(chat_id=chat_id),
                     method=set_setting_value)


def set_setting_value(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        manipulate_with_settings(message=message)

    elif text.isdigit():
        db_util.set_setting(setting_id=session.get(chat_id=chat_id,
                                                   key='setting_id'),
                            value=text)
        manipulate_with_settings(message=message)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Setting.SETTING_SETUP"),
                         reply_markup=markups.clear_markup())

    else:
        get_setting_value(chat_id=chat_id)
