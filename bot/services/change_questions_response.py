from bot.markups import get_questions_to_edit_answer
from bot.services.patterns_work.add_pattern import validate_correct_format
from bot.util import *
from database.services.patterns import get_pattern_questions, get_question_format, change_prop_format


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.ChangeQuestionResponse"))
def change_question_answer(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text='☝️ Выберите <b>шаблон</b> в котором хотите поменять ответ на вопрос',
                 reply_markup=markups.patterns(chat_id=chat_id,
                                               change_answer=True))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.PatternEditAnswer[:-2]))
def choise_pattern(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.PatternEditAnswer)
    session.set(chat_id=chat_id,
                key='pattern_id',
                value=text)
    get_question(chat_id=chat_id)


def get_question(chat_id: int):
    pattern_id = session.get(chat_id=chat_id,
                             key='pattern_id')
    send_message(chat_id=chat_id,
                 text='❓ Выберите вопрос, ответ на который хотите редактировать',
                 reply_markup=get_questions_to_edit_answer(pattern_id=pattern_id,
                                                           chat_id=chat_id))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.QuestionToEdit[:-2]))
def edit_question(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback,
                                                      callback_str=Callbacks.QuestionToEdit)

    if text == 'back':
        change_question_answer(message=callback)

    else:
        session.set(chat_id=chat_id,
                    key='question_id',
                    value=text)

        # if format_.startswith('photo') or format_.startswith('text') or format_.startswith('int'):
        get_new_limit(chat_id=chat_id)


def get_new_limit(chat_id: int, error: bool = False):
    question_id = session.get(chat_id=chat_id,
                              key='question_id')

    format_ = get_question_format(question_id=question_id)

    if error:
        text = f'Ошибка ввода формата, попробуйте ввести что-то подобное (<b>{format_[format_.find("_") + 1:]}</b>), ' \
               f'но с другими числами'

    else:
        text = f'📔 Текущий лимит на ответ <b>{format_[format_.find("_") + 1:]}</b>, ' \
               f'введите новый лимит:'

    send_message(chat_id=chat_id,
                 text=text,
                 method=set_new_limit,
                 reply_markup=markups.back(chat_id=chat_id))


def validate_new_format(chat_id: int, text: str) -> tuple:
    """
        Метод проверяющий нововведенный формат
    """
    question_id = session.get(chat_id=chat_id,
                              key='question_id')
    old_format = get_question_format(question_id=question_id)
    new_format = old_format[:old_format.find('_') + 1] + text
    return validate_correct_format(text=new_format), new_format, question_id


def set_new_limit(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id,
                      text_id='Buttons.Direction.BACK'):
        get_question(chat_id=chat_id)

    else:
        validate_status, new_format, question_id = validate_new_format(chat_id=chat_id,
                                                                       text=text)
        if validate_status:
            change_prop_format(prop_id=question_id, new_format=new_format)
            send_message(chat_id=chat_id,
                         text='😊 Формат успешно изменен',
                         reply_markup=markups.to_main_menu(chat_id=chat_id))
            # start_bot(chat_id=chat_id)

        else:
            get_new_limit(chat_id=chat_id,
                          error=True)

