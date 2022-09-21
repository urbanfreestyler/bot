from bot.util import *


def get_city(chat_id: int, for_registration: bool = False):
    callback = Callbacks.RegistrationCity if for_registration else Callbacks.ChangeCity
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Registration.GET_CITY",
                 reply_markup=markups.get_cities(callback=callback))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.RegistrationCity[:-2]))
def set_city_after_registration(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.RegistrationCity)
    delete_message(chat_id=chat_id,
                   message_id=message_id)
    answer = ''
    db_util.UserWork.add(id=chat_id,
                         username=callback.from_user.username,
                         first_name=callback.from_user.first_name,
                         available_posts=db_util.get_setting(setting_id=db_util.Constants.Settings.AMOUNT_POSTS_FOR_USUAL),
                         refresh_date=datetime.datetime.now(),)
    answer += Tx.get(chat_id=chat_id, text_id="BotMessages.Registration.END_REGISTRATION_AFTER_START")

    db_util.add_user_city(chat_id=chat_id,
                          city_id=int(text))
    answer += '\n' + Tx.get(chat_id=chat_id, text_id="BotMessages.Registration.SET_CITY")

    bot.send_message(chat_id=chat_id,
                     text=answer,
                     reply_markup=markups.main_menu(chat_id=chat_id))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.ChangeCity[:-2]))
def set_new_city(callback: CallbackQuery):

    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.ChangeCity)
    delete_message(chat_id=chat_id,
                   message_id=message_id)

    db_util.add_user_city(chat_id=chat_id,
                          city_id=int(text))

    send_message(chat_id=chat_id,
                 text_id='BotMessages.Registration.SET_CITY',
                 reply_markup=markups.main_menu(chat_id=chat_id))
