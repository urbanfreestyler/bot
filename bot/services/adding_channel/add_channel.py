from bot.util import *


@bot.message_handler(func=partial(message_data_handler, "Buttons.Menu.Partner.BecomePartner"))
@bot.message_handler(commands=Commands.PARTNER)
@get_message_info()
def become_partner(chat_id, text, message_id):
    logger.info(f'User {chat_id} in become_partner')

    session.start_become_partner(chat_id=chat_id)
