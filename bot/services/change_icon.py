from bot.util import *


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.ChangeIcon") and
                                          db_util.get_user_status(chat_id=message.from_user.id) in
                                          db_util.Constants.STATUSES[3:])
def change_icon(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id='SearchByText'),
                 reply_markup=markups._reply_markup(chat_id=chat_id,
                                                    main_menu_=True),
                 method=search_text)


def search_text(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.MAIN_MENU"):
        start_bot(message=message)

    else:
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='FindedTexts'),
                     reply_markup=markups.get_texts_from_db(text),)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.ChangeText[:-2]))
def change_icon(message: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.ChangeText)
    session.set(chat_id=chat_id,
                key='edited_message',
                value=text)
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                             text_id='SetNewIcon'),
                 method=set_new_icon)


def set_new_icon(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    botmessage_id = session.get(chat_id=chat_id,
                                key='edited_message')
    new_text = db_util.set_new_icon(new_icon=text,
                                    botmessage_id=botmessage_id)
    send_message(chat_id=chat_id,
                 text=Tx.get(chat_id=chat_id,
                                text_id='NewMessageSetup')
                 .format(new_text),
                 reply_markup=markups.main_menu(chat_id=chat_id))


