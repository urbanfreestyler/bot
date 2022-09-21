
# from bot.util import *
# from project_configuration import logging
#
#
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
