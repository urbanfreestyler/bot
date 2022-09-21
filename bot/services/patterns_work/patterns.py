from bot.services.patterns_work.add_pattern import start_create_pattern
from bot.services.patterns_work.change_pattern import start_change_pattern_title
from bot.util import *
from database import util as db_util
from database.services.patterns import PatternsWork


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Button.Patterns") and
                         db_util.get_user_status(chat_id=message.from_user.id) in db_util.Constants.STATUSES[4:])
def work_with_patterns(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} enter in work_with_patterns')
    output_patterns(chat_id=chat_id)


def output_patterns(chat_id: int, message_id: int = None, add_post: bool = False):
    if not add_post:
        admin = db_util.get_user_status(chat_id=chat_id) in db_util.Constants.STATUSES[3:]
        markup = markups.manipulate_patterns(chat_id=chat_id) if admin else markups.patterns(chat_id=chat_id)

    else:
        markup = markups.patterns(chat_id=chat_id)

    if message_id:
        edit_callback_message(chat_id=chat_id,
                              message_id=message_id,
                              text_id='ChoisePattern',
                              reply_markup=markup)

    else:
        send_message(chat_id=chat_id,
                     text_id="ChoisePattern",
                     reply_markup=markup)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.PatternAdd))
@get_message_info(callback=Callbacks.PatternAdd)
def pattern_add_start(chat_id, text, message_id):

    bot.clear_step_handler_by_chat_id(chat_id=chat_id)
    session.set(chat_id=chat_id,
                key='pattern',
                value={})

    delete_message(chat_id=chat_id,
                   message_id=message_id)
    start_create_pattern(chat_id=chat_id,
                         callback=output_patterns)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.AdminPattern))
@get_message_info(callback=Callbacks.AdminPattern)
def pattern_manipulate(chat_id, text, message_id):
    session.set(chat_id=chat_id,
                key='editable_pattern_id',
                value=text)

    edit_callback_message(chat_id=chat_id,
                          message_id=message_id,
                          text='👀 Что вы хотите сделать с шаблоном?',
                          reply_markup=markups.change_pattern(chat_id=chat_id))


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.PatternRemove))
@get_message_info(callback=Callbacks.PatternRemove)
def pattern_manipulate(chat_id, text, message_id):
    PatternsWork.remove(pattern_id=session.pop(chat_id=chat_id,
                                               key='editable_pattern_id'))
    output_patterns(chat_id=chat_id,
                    message_id=message_id)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.PatternChange))
@get_message_info(callback=Callbacks.PatternChange)
def pattern_manipulate(chat_id, text, message_id):
    start_change_pattern_title(chat_id=chat_id, callback=output_patterns)
