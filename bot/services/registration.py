from bot.services.cities import get_city
from bot.util import *


def register(chat_id: int, text_for_again_requests: str = None):
    """
        Регистрация аккаунта в системе, нужно для того чтобы мочь подать объявление
    :param chat_id:
    :param text_for_again_requests: сообщение об ошибке (если не предоставил номер)
    :return:
    """

    if not text_for_again_requests:
        text_for_again_requests = Tx.get(chat_id=chat_id, text_id="BotMessages.Registration.GET_PHONE")

    logger.info(f'User {chat_id} start register with phone')

    schedule_message(chat_id=chat_id,
                     text=text_for_again_requests,
                     reply_markup=markups.get_phone(chat_id=chat_id),
                     method=end_registration)


def end_registration(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.success(f'User {chat_id} end register with phone')

    if message.content_type == 'contact':

        phone_number = message.contact.phone_number

        if not phone_number.startswith('+'):
            phone_number = '+' + str(phone_number)

        db_util.add_phone_to_user(chat_id=chat_id,
                                  phone=phone_number)
        send_message(chat_id=chat_id,
                     text_id="BotMessages.Registration.SUCCESS",
                     reply_markup=markups.post_menu(chat_id=chat_id))

    else:
        register(chat_id=chat_id,
                 text_for_again_requests=Tx.get(chat_id=chat_id, text_id="BotMessages.Registration.ERROR_GET_PHONE"))


def register_after_start(chat_id: int, language_code: str):
    """
        Регистрация аккаунта в системе, нужно для того чтобы мочь искать
    :param chat_id:
    :return:
    """
    get_language(chat_id=chat_id,
                 language_code=language_code)


def get_language(chat_id: int, language_code: str, error: bool = False):
    if error:
        # можно добавить language code
        text = Tx.get_by_code(language=1,
                              text_id='BotMessage.ChoiseFromButtons')
    else:
        text = Tx.get_by_code(language=1,
                              text_id='BotMessage.Account.LanguageReg')

    schedule_message(chat_id=chat_id,
                     text=text,
                     reply_markup=markups.start_language_menu(chat_id=chat_id),
                     method=set_language)


def set_language(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    text_id = Tx.get_code_from_text(text=text)
    if text_id not in ('Button.Language.Russia', 'Button.Language.Uzb'):
        get_language(chat_id=chat_id,
                     language_code=message.from_user.language_code,
                     error=True)
    else:
        language = 1 if text_id == 'Button.Language.Russia' else 2
        session.set(chat_id=chat_id,
                    key='language',
                    value=language)
        get_city(chat_id=chat_id,
                 for_registration=True)
