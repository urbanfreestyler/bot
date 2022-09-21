from bot.general_controllers import start_bot
from bot.services.categories.add_category import prepare_to_add_category
from bot.util import *


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Admin.CATEGORY") and
                         db_util.get_user_status(chat_id=message.from_user.id) in db_util.Constants.STATUSES[4:])
def manipulate_with_category(message: Message = None, chat_id: int = None):
    if message:
        chat_id, text, message_id = get_info_from_message(message=message)

    logger.info(f'User {chat_id} enter in category edit')
    send_message(chat_id=chat_id,
                 text_id="ChoisePattern",
                 reply_markup=markups.patterns(chat_id=chat_id,
                                               edit_categories=True),)


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.PatternEditCategories[:-2]))
def start_choise_categories(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback, callback_str=Callbacks.PatternEditCategories)

    delete_message(message=callback)

    if text == 'back':
        start_bot(message=callback)

    else:
        session.set(chat_id=chat_id,
                    key='pattern_id',
                    value=text)
        session.set(chat_id=chat_id,
                    key='category_parent_id',
                    value=None)

        send_message(chat_id=chat_id,
                     text_id="BotMessages.Categories.MANIPULATE_WITH_CATEGORIES",
                     reply_markup=markups.categories(callback_data=Callbacks.CHANGE_CATEGORIES,
                                                     chat_id=chat_id))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.CHANGE_CATEGORIES[:-2]))
def change_category(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.CHANGE_CATEGORIES)
    if text == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        start_bot(message=callback)

    elif text.split('_')[0] in (Callbacks.Direction.LEFT, Callbacks.Direction.RIGHT):
        offset = int(text.split('_')[-1])

        edit_callback_message(chat_id=chat_id,
                              message_id=message_id,
                              reply_markup=markups.categories(offset=offset,
                                                              callback_data=Callbacks.CHANGE_CATEGORIES,
                                                              parent_id=session.get(chat_id=chat_id,
                                                                                    key='category_parent_id'),
                                                              chat_id=chat_id))

    elif text in Keyboards.Menu.Admin.CATEGORIES_EDIT[0]:
        delete_message(message=callback)
        what_you_wanna_do_with_parent_cat(chat_id=chat_id,
                                          action=text)

    else:
        markup = markups.categories(parent_id=int(text),
                                    callback_data=Callbacks.CHANGE_CATEGORIES,
                                    chat_id=chat_id)
        if len(markup.keyboard) > 1:
            session.set(chat_id=chat_id,
                        key='category_parent_id',
                        value=int(text))
            text = Tx.get(chat_id=chat_id,
                          text_id='BotMessages.AddPost.GET_CATEGORY')
            text = text[:14] + '<u>под</u>' + text[14:]
            bot.edit_message_text(chat_id=chat_id,
                                  text=text,
                                  message_id=message_id,
                                  reply_markup=markup)
        else:
            bot.send_message(chat_id=chat_id,
                             text=Tx.get(chat_id=chat_id, text_id="BotMessages.Categories.SELECTED_CATEGORY")
                             .format(db_util.get_category_by_id(category_id=int(text),
                                                                chat_id=chat_id),
                                     Tx.get(chat_id=callback.from_user.id, text_id="Buttons.Direction.BACK")))
            delete_message(chat_id=chat_id,
                           message_id=message_id)

            session.set(chat_id=chat_id,
                        key='category_parent_id',
                        value=int(text))
            schedule_message(chat_id=chat_id,
                             text=Tx.get(chat_id=chat_id, text_id="BotMessages.Categories.CHOISE_ACTION")
                             .format(db_util.get_category_by_id(category_id=int(text),
                                                                chat_id=chat_id)),
                             method=what_you_wanna_do_with_parent_cat,
                             reply_markup=markups.edit_category(chat_id=chat_id))


def what_you_wanna_do_with_parent_cat(message: Message = None, chat_id: int = 0, action: str = ''):
    """
        Работа с категориями, переход / редактирование
    """
    if message:
        chat_id = message.from_user.id
        action = Tx.get_code_from_text(text=message.text)

    if action == "Buttons.Direction.BACK":
        manipulate_with_category(message=message)

    else:
        category_id = session.get(chat_id=chat_id,
                                  key='category_parent_id')
        markup = markups.back(chat_id=chat_id)

        if action == "Buttons.Menu.CategoriesEdit.ADD":
            prepare_to_add_category(chat_id=chat_id,
                                    callback=manipulate_with_category)
            return

        elif action == "Buttons.Menu.CategoriesEdit.CHANGE":
            text, method = Tx.get(chat_id=chat_id,
                                  text_id="BotMessages.Categories.CHANGE") \
                               .format(db_util.get_category_by_id(category_id=category_id,
                                                                  chat_id=chat_id)), \
                           change_category_rus

        else:
            if db_util.get_child_categories(parent_id=category_id):
                send_message(chat_id=chat_id,
                             text_id="BotMessages.Categories.CHOISE_CATEGORY_HAVE_CHILD",
                             method=start_choise_categories,
                             reply_markup=markups.patterns(chat_id=chat_id,
                                                           edit_categories=True))
                return
            else:
                text, method = Tx.get(chat_id=chat_id, text_id="BotMessages.Categories.DELETE") \
                                   .format(db_util.get_category_by_id(category_id=category_id,
                                                                      chat_id=chat_id)), \
                               delete_category
                markup = markups.yes_or_not(chat_id=chat_id)

        schedule_message(chat_id=chat_id,
                         text=text,
                         reply_markup=markup,
                         method=method)


def change_category_rus(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text != Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        session.set(chat_id=chat_id,
                    key='change_category_rus',
                    value=text)

        send_message(chat_id=chat_id,
                     text_id="BotMessages.Categories.CHANGE_UZB",
                     method=change_category_uzb)

    else:
        manipulate_with_category(message=message)


def change_category_uzb(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text != Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        parent_id = session.get(chat_id=chat_id, key='category_parent_id')
        db_util.change_category(parent_id=parent_id,
                                rus_title=session.get(chat_id=chat_id,
                                                      key='change_category_rus'),
                                uzb_title=text)

        send_message(chat_id=chat_id,
                     text_id="BotMessages.Categories.SUCCESS_CHANGE",
                     reply_markup=markups.clear_markup())

    manipulate_with_category(message=message)


def delete_category(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text != Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):

        parent_id = session.get(chat_id=chat_id,
                                key='category_parent_id')

        if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.YES"):
            category_title = db_util.get_category_by_id(category_id=parent_id,
                                                        chat_id=chat_id)
            db_util.remove_category(parent_id=parent_id)
            send_message(chat_id=chat_id,
                         text=Tx
                         .get(chat_id=chat_id, text_id="BotMessages.Categories.SUCCESS_DELETE")
                         .format(category_title),
                         reply_markup=markups.clear_markup())

    manipulate_with_category(message=message)
