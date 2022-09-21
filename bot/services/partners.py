from bot.util import *
from project_configuration import logging


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id, text_id="Buttons"
                                                                                                       ".Account"
                                                                                                       ".PARTNER"))
@bot.message_handler(commands=Commands.PARTNER)
@logging()
def partners(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} entering for_partners')
    if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
        send_message(chat_id=chat_id,
                     text_id="Buttons.Account.FOR_PARTNER",
                     reply_markup=markups.partner_menu(chat_id=chat_id))