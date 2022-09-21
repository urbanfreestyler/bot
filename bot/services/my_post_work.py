from bot.services.output_posts import get_moderation_post_for_usual, get_active_post_for_usual, \
    get_deleted_post_for_usual
from bot.util import *
from project_configuration import logging


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".MY_POSTS"))
@bot.message_handler(commands=Commands.MY_POST)
@logging()
def my_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} use my post')
    if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
        send_message(chat_id=chat_id,
                     text_id="Buttons.Account.MY_POSTS",
                     reply_markup=markups.post_menu(chat_id=chat_id))


# @bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons."
#                                                                                                        "Menu."
#                                                                                                        "Channel"))
# @bot.message_handler(commands=Commands.MY_CHANNEL)
# @logging()
# def my_channels(message: Message):
#     chat_id, text, message_id = get_info_from_message(message=message)
#     logger.info(f'User {chat_id} use my channel')
#     if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
#         send_message(chat_id=chat_id,
#                      text_id="Buttons.Account.MY_CHANNELS",
#                      reply_markup=markups.channel_menu(chat_id=chat_id))


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu"
                                                                                                       ".Post.MODERATE"))
@bot.message_handler(func=lambda message: message.text == '/' + Commands.MODERATE[0] and
                                          db_util.get_user_status(chat_id=message.from_user.id) in
                                          db_util.Constants.STATUSES[:3])
def moderate_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    get_moderation_post_for_usual(chat_id=chat_id)
    logger.info(f'User {chat_id} use moderate post')


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu"
                                                                                                       ".Post.POSTED"))
@bot.message_handler(commands=Commands.POSTED)
def moderate_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    get_active_post_for_usual(chat_id=chat_id)
    logger.info(f'User {chat_id} use posted post')


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu"
                                                                                                       ".Post.DELETED"))
@bot.message_handler(commands=Commands.DELETED)
def moderate_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    get_deleted_post_for_usual(chat_id=chat_id)
    logger.info(f'User {chat_id} use deleted post')
