from bot.util import *
from database.services.patterns import PatternsWork


output_patterns_callback_func = None


def start_create_pattern(chat_id: int, callback):
    global output_patterns_callback_func
    output_patterns_callback_func = callback
    get_russian_pattern_title(chat_id=chat_id)


def get_russian_pattern_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text='🇷🇺 Введите название <b>шаблона</b> на Русском',
                 method=set_russian_pattern_title,
                 reply_markup=markups.back(chat_id=chat_id))


def set_russian_pattern_title(message: Message = None):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='pattern___rus',
                    value=text)
        get_uzb_pattern_title(chat_id=chat_id)

    else:
        output_patterns_callback_func(chat_id=chat_id)


def get_uzb_pattern_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text="🇺🇿 Введите название <b>шаблона</b> на Узбекском",
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_uzb_pattern_title)


def set_uzb_pattern_title(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='pattern___uzb',
                    value=text)
        session.set(chat_id=chat_id,
                    key='photo_in_pattern',
                    value=False)
        session.set(chat_id=chat_id,
                    key='questions',
                    value=[])
        get_questions(message=message)

    else:
        get_russian_pattern_title(chat_id=chat_id)


def get_questions(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    session.set(chat_id=chat_id,
                key='question',
                value={})
    get_russian_question(chat_id=chat_id)


def get_russian_question(chat_id: int):
    text = '🇷🇺 Введите {} <b>вопрос</b> на русском'

    questions = session.get(chat_id=chat_id,
                            key='questions')
    amount_questions = len(questions)
    send_message(chat_id=chat_id,
                 text=text.format(amount_questions + 1),
                 reply_markup=markups.back(chat_id=chat_id) if not amount_questions else None,
                 method=set_russian_question)


def set_russian_question(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='question___rus',
                    value=text)
        get_uzb_question(chat_id=chat_id)

    else:
        get_uzb_pattern_title(chat_id=chat_id)


def get_uzb_question(chat_id: int):
    send_message(chat_id=chat_id,
                 text="🇺🇿 Введите <b>вопрос</b> на Узбекском",
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_uzb_question)


def set_uzb_question(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='question___uzb',
                    value=text)
        get_format_question(chat_id=chat_id)

    else:
        get_russian_question(chat_id=chat_id)


def get_format_question(chat_id: int, error: Union[bool, str] = False):
    text = "🧰 Введите формат данных.\n" \
           "Пример:\n" \
           "<code>text_10</code>, где:\n" \
                "<code>text</code> - любой текст,\n" \
                "<code>10</code> - максимальное количество символов в данном тексте;\n\n" \
           "<code>int_-1_100</code>, где:\n" \
                "<code>int</code> - любая цифра,\n" \
                "<code>-1</code> - минимальное значение введённой цифры,\n" \
                "<code>100</code> - максимальное значение введенной цифры;\n\n" \
           "<code>photo_5</code>, где:\n" \
                "<code>photo</code> - фотография,\n" \
                "<code>5</code> - количество фотографий;\n" \
           "<code>geo</code> - взять гео данные предоставленные пользователем;\n" \
           "<code>contact</code> - взять контакт а через контакт номер телефона пользователя;"

    if error == 'photo':
        text = '😖 Фото <u><b>уже</b></u> добавлены, выберите другой формат \n\n' + text

    elif error:
        text = '😖 Введите корректный формат данных\n\n' + text

    send_message(chat_id=chat_id,
                 text=text,
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_format_question)


def validate_correct_format(text: str) -> bool:
    """
        Валидация правильности ввода пользователя
    """
    keywords = text.split('_')
    type_ = keywords[0]

    if type_ not in ('int', 'text', 'photo', 'geo', 'contact'):
        return False

    if type_ in ('geo', 'contact'):
        return True

    if type_ == 'int':
        try:
            if len(keywords[1:]) == 2:
                return bool(int(keywords[1]) and int(keywords[2]))
        except:
            return False

    if type_ in ('photo', 'text'):
        try:
            return 0 < int(keywords[1]) <= (10 if type_ == 'photo' else 1024)
        except:
            return False


def set_format_question(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):

        photo_exists = session.get(chat_id=chat_id,
                                   key='photo_in_pattern')

        if validate_correct_format(text=text):
            session.set(chat_id=chat_id,
                        key='question___format_',
                        value=text)

            if text.startswith('photo') and photo_exists:
                get_format_question(chat_id=chat_id,
                                    error='photo')
                return

            elif text.startswith('photo'):
                session.set(chat_id=chat_id,
                            key='photo_in_pattern',
                            value=True)

            get_russian_list_title(chat_id=chat_id)

        else:
            get_format_question(chat_id=chat_id,
                                error=True)

    else:
        get_uzb_question(chat_id=chat_id)


def get_russian_list_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text='🇷🇺 Введите название <b>параметра</b> на Русском',
                 method=set_russian_list_title,
                 reply_markup=markups.back(chat_id=chat_id))


def set_russian_list_title(message: Message = None):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='question___rus_title_in_list',
                    value=text)
        get_uzb_list_title(chat_id=chat_id)

    else:
        get_format_question(chat_id=chat_id)


def get_uzb_list_title(chat_id: int):
    send_message(chat_id=chat_id,
                 text="🇺🇿 Введите название <b>параметра</b> на Узбекском",
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_uzb_list_title)


def set_uzb_list_title(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if text != Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        session.set(chat_id=chat_id,
                    key='question___uzb_title_in_list',
                    value=text)
        # get_questions(message=message)
        session.update_key(chat_id=chat_id,
                           key='questions',
                           value=session.pop(chat_id=chat_id, key='question'),
                           method='append')
        send_message(chat_id=chat_id,
                     text='😊 Вопрос успешно добавлен\n'
                          '🧐 Хотите ли ещё добавить вопросов?',
                     reply_markup=markups.yes_or_not(chat_id=chat_id,
                                                     back_=False),
                     method=will_be_next)
    else:
        get_russian_list_title(chat_id=chat_id)


def will_be_next(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id,
                      text_id='Buttons.YES'):
        get_questions(message=message)

    # elif text == Tx.get(chat_id=chat_id,
    #                     text_id='Buttons.NO'):
    else:
        end_create_pattern(chat_id=chat_id)


def end_create_pattern(chat_id: int):
    pattern_title = session.get(chat_id=chat_id,
                                key='pattern')['rus']
    PatternsWork.create(chat_id=chat_id)
    send_message(chat_id=chat_id,
                 text=f'😊 Шаблон "{pattern_title}" успешно добавлен')
    output_patterns_callback_func(chat_id=chat_id)
