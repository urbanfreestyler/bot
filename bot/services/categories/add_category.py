from bot.util import *


callback_to_manipulate = None


def prepare_to_add_category(chat_id: int, callback):
    global callback_to_manipulate
    callback_to_manipulate = callback

    get_category_title(chat_id=chat_id)


def get_category_title(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='category_parent_id')
    if category_id:
        text = Tx.get(chat_id=chat_id,
                      text_id="BotMessages.Categories.ADD") \
            .format(db_util.get_category_by_id(category_id=category_id,
                                               chat_id=chat_id))

    else:
        text = Tx.get(chat_id=chat_id,
                      text_id="BotMessages.Categories.ADD_WITHOUT_PARENT")

    send_message(chat_id=chat_id,
                 text=text,
                 method=set_category_title,
                 reply_markup=markups.back(chat_id=chat_id))


def set_category_title(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        callback_to_manipulate(message=message)

    else:
        session.set(chat_id=chat_id,
                    key='category___title_rus',
                    value=text)
        get_category_title_uzb(chat_id=chat_id)


def get_category_title_uzb(chat_id: int):
    send_message(chat_id=chat_id,
                 text_id='BotMessages.Categories.ADD_UZB',
                 method=set_category_title_uzb,
                 reply_markup=markups.back(chat_id=chat_id))


def set_category_title_uzb(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_category_title(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='category___title_uzb',
                    value=text)
        get_status(chat_id=chat_id)


def get_status(chat_id: int):
    send_message(chat_id=chat_id,
                 text='❓ Будет ли вопрос о статусе товара? (📦 Новое и 🥡 Б/У)',
                 method=set_status,
                 reply_markup=markups.set_question_about_status(chat_id=chat_id))


def set_status(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_category_title_uzb(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='category___status',
                    value=text == Tx.get(chat_id=chat_id, text_id='Button.SetStatus'))
        get_buy_status(chat_id=chat_id)


def get_buy_status(chat_id: int):
    send_message(chat_id=chat_id,
                 text='❓ Будет ли вопрос о <b>купле / продаже</b> товара?',
                 method=set_buy_status,
                 reply_markup=markups.yes_or_not(chat_id=chat_id))


def set_buy_status(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='category___buy_status',
                    value=text == Tx.get(chat_id=chat_id, text_id='Buttons.YES'))
        add_category(chat_id=chat_id)


def add_category(chat_id: int):
    new_category = session.get(chat_id=chat_id,
                               key='category')

    new_uzb, new_rus = new_category['title_rus'], new_category['title_uzb']

    if db_util.add_category(parent_id=session.get(chat_id=chat_id,
                                                  key='category_parent_id'),
                            new_category=new_category,
                            pattern_id=session.get(chat_id=chat_id,
                                                   key='pattern_id')):
        text = Tx.get(chat_id=chat_id,
                      text_id="BotMessages.Categories.SUCCESS_ADD_WITHOUT") \
            .format(new_rus, new_uzb)
    else:
        text = Tx.get(chat_id=chat_id,
                      text_id="BotMessages.Categories.UNSUCCESS_ADD")

    send_message(chat_id=chat_id,
                 text=text,
                 reply_markup=markups.clear_markup())
    callback_to_manipulate(chat_id=chat_id)
