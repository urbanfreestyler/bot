from bot.util import *
from project_configuration import logging

import daemon_support.temp_storage as temp_stor


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Activity"))
@logging()
def get_statistic(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    msg = send_message(chat_id=chat_id,
                       text=Tx.get(chat_id=chat_id,
                                   text_id='BotMessages.Activity.Statictic')
                       .format(temp_stor.get_amount_players(),
                               db_util.StatisticWork.get_week(),
                               db_util.StatisticWork.get_month()),
                       reply_markup=markups.main_menu(chat_id=chat_id))
