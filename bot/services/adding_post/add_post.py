from bot.services.adding_post.get_photos import get_pictures
from bot.services.adding_post.util import validate_input
from bot.services.output_posts import format_post_from_dict
from bot.services.patterns_work.patterns import output_patterns
from bot.services.registration import register
from bot.util import *
from database.models import Categories, Channel, PatternsMultiLang
from database.services.patterns import get_pattern_questions
import time


@bot.message_handler(func=partial(message_data_handler, "Buttons.Menu.Post.ADD"))
@bot.message_handler(commands=Commands.ADD_POST)
@get_message_info
def add_post(chat_id, text, message_id):
    logger.info(f'User {chat_id} in add_post')

    if not Validator.user_phone(chat_id=chat_id):
        register(chat_id=chat_id)

    elif Validator.check_available_posts(chat_id=chat_id):
        start_quest(chat_id=chat_id)

    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.AddPost.NOT_AVAILABLE_POST_TODAY",
                     reply_markup=markups.main_menu(chat_id=chat_id))


def start_quest(chat_id: int):
    session.start_add_post(chat_id=chat_id)
    output_patterns(chat_id=chat_id, add_post=True)


@bot.callback_query_handler(func=partial(message_data_handler, Callbacks.Pattern))
@get_message_info(callback=Callbacks.Pattern)
def set_pattern(chat_id, text, message_id):
    delete_message(chat_id=chat_id,
                   message_id=message_id)

    if text == 'back':
        start_bot(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='pattern_id',
                    value=text)
        prepare_for_get_category(chat_id=chat_id)


def prepare_for_get_category(chat_id: int):
    send_message(chat_id=chat_id,
                 text_id="BotMessages.AddPost.GET_CATEGORY",
                 reply_markup=markups.categories(add_post=True,
                                                 chat_id=chat_id))


@bot.callback_query_handler(func=lambda callback: callback.data.startswith(Callbacks.CATEGORY[:-2]) and
                                                  session.get(chat_id=callback.from_user.id,
                                                              key='add_post'))
def get_category(callback: CallbackQuery):
    chat_id, text, message_id = get_info_from_message(message=callback, callback_str=Callbacks.CATEGORY)

    if text == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        # start_bot(message=callback)
        start_quest(chat_id=chat_id)

    elif text[:text.find('_')] in (Callbacks.Direction.LEFT, Callbacks.Direction.RIGHT):
        offset = int(text[text.find('_') + 1:])

        edit_callback_message(chat_id=chat_id,
                              message_id=message_id,
                              reply_markup=markups.categories(offset=offset,
                                                              parent_id=session.get(chat_id=chat_id,
                                                                                    key='category_parent_id'),
                                                              add_post=session.get(chat_id=chat_id,
                                                                                   key='add_post'),
                                                              chat_id=chat_id), )

    else:
        markup = markups.categories(parent_id=int(text),
                                    add_post=session.get(chat_id=callback.from_user.id,
                                                         key='add_post'),
                                    chat_id=chat_id)
        if len(markup.keyboard) > 1:
            session.set(chat_id=chat_id,
                        key='category_parent_id',
                        value=int(text))
            text = Tx.get(chat_id=chat_id,
                          text_id="BotMessages.AddPost.GET_CATEGORY")
            text = text[:14] + '<u>под</u>' + text[14:]
            bot.edit_message_text(chat_id=chat_id,
                                  text=text,
                                  message_id=message_id,
                                  reply_markup=markup)
        else:
            send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.AddPost.SELECTED_CATEGORY")
                         .format(db_util.get_category_by_id(category_id=int(text),
                                                            chat_id=chat_id),
                                 Tx.get(chat_id=callback.from_user.id, text_id="Buttons.Direction.BACK")))

            session.set(chat_id=chat_id,
                        key='post___category_id',
                        value=int(text))
            delete_message(chat_id=chat_id,
                           message_id=message_id)
            start_questions(chat_id=chat_id)


def get_price_question(chat_id: int, questions: list):
    for question in questions:
        if 'цена' in question[-1].lower():
            return session.set(chat_id=chat_id,
                               key='price',
                               value=True)


def start_questions(chat_id: int):
    questions = get_pattern_questions(pattern_id=session.get(chat_id=chat_id,
                                                             key='pattern_id'),
                                      chat_id=chat_id)

    get_price_question(chat_id=chat_id,
                       questions=questions)

    session.set(chat_id=chat_id,
                key='pattern_questions',
                value=questions)
    session.set(chat_id=chat_id,
                key='previous_questions',
                value=[])

    prepare_question(chat_id=chat_id)


def prepare_question(chat_id):
    questions: list = session.get(chat_id=chat_id,
                                  key='pattern_questions')

    question = questions.pop(0)
    # удаляем первый из вопросов
    session.set(chat_id=chat_id,
                key='pattern_questions',
                value=questions)
    # текущий вопрос (для формата и пропсов)
    session.set(chat_id=chat_id,
                key='current_question',
                value=question)

    get_question(chat_id=chat_id)


def back_question(chat_id: int, from_end: bool = False) -> list:
    """
        Смена вопросов на один назад
    """
    questions: list = session.get(chat_id=chat_id,
                                  key='pattern_questions')
    previous_questions: list = session.get(chat_id=chat_id,
                                           key='previous_questions')
    question = previous_questions.pop()

    if not from_end:
        questions = [session.get(chat_id=chat_id, key='current_question')] + questions

    session.set(chat_id=chat_id,
                key='pattern_questions',
                value=questions)
    session.set(chat_id=chat_id,
                key='previous_questions',
                value=previous_questions)
    session.set(chat_id=chat_id,
                key='current_question',
                value=question)
    return question


def get_question(chat_id: int,
                 error_text: str = '',
                 back: bool = False,
                 from_end: bool = False):
    """
        Выдаем новый вопрос в методе,
        back - возвращаем на один вопрос назад;
        for_end - начинаем выводить вопросы после их полного прохождения
            (если пользователь в статусе нажал назад)
    """

    if back:
        if session.get(chat_id=chat_id,
                       key='previous_questions'):
            question = back_question(chat_id, from_end=from_end)
        else:
            prepare_for_get_category(chat_id=chat_id)
            return

    else:
        question = session.get(chat_id=chat_id, key='current_question')

    if question[1].split('_')[0] == 'photo':
        get_pictures(chat_id=chat_id,
                     callback_to_next=to_next_question,
                     callback_to_back=get_question)
        return

    if question[1] == 'contact':
        markup = markups.get_phone(chat_id=chat_id,
                                   back_=True)

    # elif question[1] == 'geo':
    #     markup = markups.get_current_geo(chat_id=chat_id,
    #                                      skip=True)

    else:
        markup = markups.back(chat_id=chat_id)

    send_message(chat_id=chat_id,
                 text=error_text if error_text else question[2],
                 method=set_question,
                 reply_markup=markup)


def set_question(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id,
                      text_id="Buttons.Direction.BACK"):
        get_question(chat_id=chat_id,
                     back=True)
        return

    status, error_text, *args = validate_input(text=text,
                                               chat_id=chat_id,
                                               message_type=message.content_type)

    if status:
        current_question = session.get(chat_id=chat_id,
                                       key='current_question')
        prop_id, prop_title = current_question[0], current_question[3].lower()

        if message.content_type == 'location':

            value = [message.location.longitude, message.location.latitude]

            session.set(chat_id=chat_id,
                        key='post___geo',
                        value={'longitude': value[0],
                               'latitude': value[1]})

        elif message.content_type == 'contact':
            value = str(message.contact.phone_number)
            value = value if '+' in value else f'+{value}'

        else:
            value = text

        if text not in (Tx.get(chat_id=chat_id, text_id='Buttons.Direction.CONTINUE'),
                        Tx.get(chat_id=chat_id, text_id='skip')):
            session.set(chat_id=chat_id,
                        key=f'post___{prop_id}',
                        value=value)

        if 'цена' in prop_title:
            get_currency(chat_id=chat_id)

        elif 'narx' in prop_title:
            get_currency(chat_id=chat_id)
        else:
            to_next_question(chat_id=chat_id)

    else:
        get_question(chat_id=chat_id,
                     error_text=Tx.get(chat_id=chat_id,
                                       text_id=error_text).format(*args))


def get_currency(chat_id: int):
    send_message(chat_id=chat_id,
                 text_id="choise_currency",
                 method=set_currency,
                 reply_markup=markups.get_currencies(chat_id=chat_id))


def set_currency(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    dollar = Tx.get(chat_id=message.from_user.id, text_id="dollar")
    currency = text == dollar
    currency = dollar if currency else Tx.get(chat_id=message.from_user.id, text_id="summ")

    session.set(chat_id=chat_id,
                key='post___currency',
                value=currency)
    to_next_question(chat_id=chat_id)


def to_next_question(chat_id: int):
    session.update_key(chat_id=chat_id,
                       key='previous_questions',
                       value=session.get(chat_id=chat_id,
                                         key='current_question'),
                       method='append')

    if session.get(chat_id=chat_id,
                   key='pattern_questions'):
        prepare_question(chat_id=chat_id)

    else:
        pre_status(chat_id=chat_id)


def pre_status(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='post')['category_id']

    if db_util.exists_status(category_id=category_id):
        get_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='post___status',
                    value=True)
        # get_keywords(chat_id=chat_id)
        pre_buy_status(chat_id=chat_id)


def get_status(chat_id: int):
    send_message(chat_id=chat_id,
                 text_id="Choise Status",
                 reply_markup=markups.get_status_product(chat_id=chat_id,
                                                         back_=True),
                 method=set_status)


def set_status(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        get_question(chat_id=chat_id,
                     back=True,
                     from_end=True)

    else:
        session.set(chat_id=chat_id,
                    key='post___status',
                    value=text == Tx.get(chat_id=chat_id, text_id='Button.New'))
        # get_keywords(chat_id=chat_id)
        pre_buy_status(chat_id=chat_id)


def pre_buy_status(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='post')['category_id']

    if db_util.exists_buy_status(category_id=category_id):
        get_buy_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='post___buy_status',
                    value=False)
        get_keywords(chat_id=chat_id)


def get_buy_status(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='post')['category_id']

    markup = markups \
        .get_buy_status(chat_id=chat_id,
                        back_=db_util.exists_status(category_id=category_id))

    send_message(chat_id=chat_id,
                 text_id="choise_buy_status",
                 reply_markup=markup,
                 method=set_buy_status)


def set_buy_status(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        pre_status(chat_id=chat_id)

    else:
        session.set(chat_id=chat_id,
                    key='post___buy_status',
                    value=text == Tx.get(chat_id=chat_id, text_id='Buy'))
        get_keywords(chat_id=chat_id)


def get_keywords(chat_id: int):
    category_id = session.get(chat_id=chat_id,
                              key='post')['category_id']

    back = db_util.exists_status(category_id=category_id) or db_util.exists_buy_status(category_id=category_id)

    send_message(chat_id=chat_id,
                 text_id="get_keywords",
                 method=set_keywords,
                 reply_markup=markups.skip_keyboard(chat_id=chat_id,
                                                    back_=back))


def set_keywords(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):

        category_id = session.get(chat_id=chat_id,
                                  key='post')['category_id']

        if db_util.exists_buy_status(category_id=category_id):
            pre_buy_status(chat_id)

        else:
            pre_status(chat_id=chat_id)

        return

    elif text != Tx.get(chat_id=message.from_user.id, text_id="skip"):

        if text:
            keywords = tuple(word.strip().lower() for word in text.split(',') if word)

        else:
            keywords = tuple()

        session.set(chat_id=chat_id,
                    key='post___keywords',
                    value=keywords)

    else:
        session.set(chat_id=chat_id,
                    key='post___keywords',
                    value=[])

    choose_channels_for_post(chat_id=chat_id)
    # posting_end(chat_id=chat_id)


def choose_channels_for_post(chat_id: int):
    pattern_id = session.get(chat_id=chat_id, key='pattern_id')
    send_message(chat_id=chat_id,
                 text_id='Buttons.Post.ChooseChannel',
                 reply_markup=markups.channels(chat_id=chat_id,
                                               pattern_id=pattern_id))


global sum
sum = 0

global selected_channels
selected_channels = []

global channel_list
channel_list = ''


@bot.callback_query_handler(func=lambda call: True)
def channel_choice_updater(call):
    global sum
    for channel in Channel.select():
        global selected_channels
        global channel_list
        selected_channels = []

        pattern_id = session.get(chat_id=call.message.chat.id, key='pattern_id')
        if call.data == str(channel.id):
            if not channel.selected:
                bot.answer_callback_query(call.id, 'Выбран канал ' + channel.name)
                selected_channels.append(channel.name)
                if not channel_list == '':
                    channel_list += '\n' + channel.name
                else:
                    channel_list = Tx.get(chat_id=call.message.chat.id,
                                          text_id="BotMessages.SelectedChannels") + '\n' + channel.name
                channel.selected = True
                channel.save()
                bot.edit_message_text(message_id=call.message.id,
                                      chat_id=call.message.chat.id,
                                      text=Tx.get(chat_id=call.message.chat.id,
                                                  text_id="Buttons.Post.ChooseChannel") +
                                           '\n' + channel_list,
                                      reply_markup=markups.channels(chat_id=call.message.chat.id,
                                                                    pattern_id=pattern_id))

            else:
                bot.answer_callback_query(call.id, 'Отменён выбор канала ' + channel.name)
                channel.selected = False

                channel_list = channel_list.replace('\n' + channel.name, '')
                channel_list = '' if channel_list == Tx.get(chat_id=call.message.chat.id,
                                                            text_id="BotMessages.SelectedChannels") else channel_list

                channel.save()
                bot.edit_message_text(message_id=call.message.id,
                                      chat_id=call.message.chat.id,
                                      text=Tx.get(chat_id=call.message.chat.id,
                                                  text_id="Buttons.Post.ChooseChannel") +
                                           '\n' + channel_list,
                                      reply_markup=markups.channels(chat_id=call.message.chat.id,
                                                                    pattern_id=pattern_id))

    if call.data == Callbacks.Continue:
        for channel in Channel.select().where(Channel.selected == True):
            selected_channels.append(channel.id)
            sum += channel.price_for_post
            channel.selected = False
            channel.save()
        session.set(chat_id=call.message.chat.id,
                    key='post___selected_channels',
                    value=selected_channels)

        user = db_util.Users.get(id=call.message.chat.id)
        if not selected_channels or sum == 0:

            posting_end(chat_id=call.message.chat.id)
        else:
            selected_channels = []
            send_message(chat_id=call.message.chat.id,
                         text=Tx.get(chat_id=call.message.chat.id, text_id="Button.Payment").format(user.balance, sum),
                         reply_markup=markups.payment(chat_id=call.message.chat.id))


@bot.message_handler(func=partial(message_data_handler, "Buttons.Pay"))
def payment(message: Message):
    global sum
    global selected_channels
    chat_id, text, message_id = get_info_from_message(message=message)
    if text == Tx.get(chat_id=message.from_user.id, text_id='Buttons.Pay'):
        user = db_util.Users.get(id=chat_id)
        if user.balance >= sum:
            user.balance -= sum
            user.save()

            for x in selected_channels:
                channel = Channel.get(Channel.id == int(x))
                sum += channel.price_for_post
                channel_owner = db_util.Users.get(id=channel.channel_owner_id)
                # TODO
                channel_owner.balance += channel.price_for_post
                channel_owner.save()
            sum = 0
            send_message(chat_id, "Вы успешно оплатили за публикацию объявления!")
            posting_end(chat_id=chat_id)

        else:
            send_message(chat_id=chat_id,
                         text=Tx.get(chat_id, text_id='Buttons.Payment.NotEnoughMoney'),
                         reply_markup=markups.payment(chat_id))


def posting_end(chat_id: int):
    format_post_from_dict(chat_id=chat_id, )
    send_message(chat_id=chat_id,
                 text_id="BotMessages.PostOut.PREVIEW",
                 reply_markup=markups.preview(chat_id=chat_id),
                 method=post_publication)


def post_publication(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Menu.Preview.RESET"):

        send_message(chat_id=chat_id,
                     text_id='confirm_to_delete_preview',
                     reply_markup=markups.get_reedit_post_menu(chat_id=chat_id),
                     method=question_before_restart)

    else:
        session.set(chat_id=chat_id,
                    key='add_post',
                    value=False)

        moderate_status = db_util.publicate_post(chat_id=chat_id)

        text = Tx.get(chat_id=chat_id,
                      text_id="BotMessages.PostOut.ON_MODERATE" if moderate_status else
                      "BotMessages.PostOut.ON_PUBLICATE")

        bot.send_message(chat_id=chat_id,
                         text=text,
                         reply_markup=markups.main_menu(chat_id=chat_id))


def question_before_restart(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=chat_id,
                      text_id='post_it'):
        post_publication(message=message)

    else:
        start_quest(chat_id=chat_id)

