from bot.util import session, Tx


def validate_input(text: str, chat_id: int, message_type: str) -> tuple:
    format_: str = session.get(chat_id=chat_id,
                               key='current_question')[1]
    format_: list = format_.split('_')

    if format_[0] == 'text':
        try:
            if len(text) <= int(format_[1]):
                return True, ''
            else:
                return False, 'max_amount_symbols', format_[1]
        except:
            return False, 'max_amount_symbols', format_[1]

    elif format_[0] == 'int':
        try:

            if int(format_[1]) <= int(text) <= int(format_[2]):
                return True, ''
            else:
                return False, 'available_range', format_[1], format_[2]

        except Exception:
            return False, 'only_digit', ''

    elif format_[0] == 'geo' and message_type in ('location', 'text'):

        if message_type == 'location':
            return True, ''

        elif text == Tx.get(chat_id=chat_id, text_id='skip'):
            return True, ''

        else:
            return False, 'available_geo'

    elif format_[0] == 'contact':

        if message_type == 'contact':
            return True, ''

        else:
            return False, 'available_contact'

    elif format_[0] == message_type:
        return True, ''
