from database.models import BotMessages
from database.services.session import SessionWork as session


class Text:
    @staticmethod
    def get(chat_id: int, text_id: str) -> str:
        """
            Для получения текста из бд на нужном языке
        :param chat_id:
        :param text_id:
        :return:
        """
        try:
            language = session.get(chat_id=chat_id,
                                   key='language')
        except Exception as e:
            language = 1

        if finded_element := BotMessages.get_or_none(BotMessages.text_id == text_id,
                                                     BotMessages.language == language if language else 1):
            return finded_element.text.replace('\\n', '\n')

        else:
            return BotMessages\
                .get(BotMessages.text_id == text_id,
                     BotMessages.language == 1)\
                .text\
                .replace('\\n', '\n')

    @staticmethod
    def get_code_from_text(text: str) -> str:
        try:
            return BotMessages.get(BotMessages.text == text).text_id
        except Exception as e:
            return False

    @staticmethod
    def get_by_code(text_id: str, language: int = 1) -> str:
        return BotMessages.get(BotMessages.text_id == text_id,
                               BotMessages.language == language).text


def get_texts(text: str):
    return BotMessages.filter(BotMessages.text.contains(text))


def set_new_icon(new_icon: str, botmessage_id: str) -> str:
    message: BotMessages = BotMessages.get(id=botmessage_id)
    message.text = new_icon + message.text[message.text.find(' '):]
    message.save()
    return message.text
