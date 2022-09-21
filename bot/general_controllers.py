from bot.services.registration import register_after_start
from bot.util import *
import daemon_support.temp_storage as temp_stor


# @bot.message_handler(commands=Commands.HELP)
# def help(message: Message):
#     chat_id, text, message_id = get_info_from_message(message=message)
#     # status = db_util.get_user_status(chat_id=chat_id)
#     logger.info(f'User {chat_id} use {text}')
#     bot.send_message(chat_id=chat_id,
#                      text=Tx.get(chat_id=chat_id,
#                                  text_id='BotMessages.Help.START'))
