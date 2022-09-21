from bot.util import *
from database.services.patterns import PatternsWork


output_patterns_callback_func = None


def start_change_pattern_title(chat_id: int, callback):
    global output_patterns_callback_func
    output_patterns_callback_func = callback
    get_russian_new_title(chat_id=chat_id)


def get_russian_new_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text='🇷🇺 Введите название на Русском',
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_russian_new_title)


def set_russian_new_title(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='new_pattern_rus_title',
                    value=text)
        get_uzb_new_title(chat_id=chat_id)

    else:
        output_patterns_callback_func(chat_id=chat_id)


def get_uzb_new_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text='🇺🇿 Введите название на Узбекском',
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_uzb_new_title)


def set_uzb_new_title(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='new_pattern_uzb_title',
                    value=text)
        # get_uzb_new_title()
        end_editing_pattern(chat_id=chat_id)

    else:
        get_russian_new_title(chat_id=chat_id)


def end_editing_pattern(chat_id: int):
    PatternsWork.change(chat_id=chat_id)
    output_patterns_callback_func(chat_id=chat_id)
