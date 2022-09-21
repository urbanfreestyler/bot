import time
from telebot.types import CallbackQuery, InputMediaPhoto
from database.models import Post, Categories, Channel, PatternsMultiLang
from bot.util import *
from database.services.patterns import get_pattern_props_by_category, get_pattern_questions, \
    get_product_props_with_names
from database.services.users import UserWork

from global_var import CHANNEL_ID_62
import json


def get_photos_from_dict(photos: list) -> list[InputMediaPhoto]:
    result_photos = []
    for photo_index, photo in enumerate(photos):
        with open(photo, 'rb') as file:
            result_photos.append(InputMediaPhoto(media=file.read()))
    return result_photos


global count
count = 0


def format_post_from_dict(chat_id: int):
    global text
    post_data: dict = session.get(chat_id=chat_id,
                                  key='post')
    # phone = UserWork.get_phone(chat_id=chat_id)
    props = get_pattern_questions(pattern_id=session.get(chat_id=chat_id, key='pattern_id'),
                                  chat_id=chat_id)
    markup, text = None, ''

    for prop in props:
        type_, *other_args = prop[1].split('_')

        post_value = post_data.get(str(prop[0])) if type_ != 'photo' else post_data.get('photos')

        if type_ in ('text', 'int', 'contact'):

            if 'цена' in prop[3].lower():
                # print(post_data["currency"])
                text += f'<b>{prop[3]}</b>: {post_value} {post_data["currency"]}\n'
            elif 'narx' in prop[3].lower():
                text += f'\n<b>{prop[3]}</b>: {post_value} {post.currency}\n'
            else:
                text += f'<b>{prop[3]}</b>: {post_value}\n'

        # elif type_ == 'photo' and post_value:
        #     bot.send_media_group(chat_id=chat_id,
        #                          media=get_photos_from_dict(photos=post_value))

        # elif type_ == 'geo' and post_value:
        #     long, lati = post_value
        #     markup = markups.get_geo(chat_id=chat_id,
        #                              long=long,
        #                              lati=lati)

    # text += f'\n<b>✒️ Ключевые слова:</b> {", ".join(post_data["keywords"])}' if post_data['keywords'] else ''
    text += Tx.get(chat_id=chat_id, text_id='keywords_prop').format(", ".join(post_data["keywords"])) if \
        post_data['keywords'] else ''

    for prop in props:
        type_, *other_args = prop[1].split('_')

        post_value = post_data.get(str(prop[0])) if type_ != 'photo' else post_data.get('photos')
        if type_ == 'photo' and post_value:
            bot.send_media_group(chat_id=chat_id,
                                 media=get_photos_from_dict(photos=post_value))

    markup = markups.reactions_to_post(counter=count)

    send_message(chat_id=chat_id,
                 text=text if text else '_',
                 reply_markup=markup)


def get_photos_from_db(post: Post):
    text, markup = '', None

    publicator: db_util.Users = post.owner

    props = get_product_props_with_names(post=post)

    for prop in props:
        type_, *other_args = prop[1].split('_')

        post_value = prop[2]

        if type_ in ('text', 'int', 'contact'):

            if 'цена' in prop[0].lower():
                text += f'\n<b>{prop[0]}</b>: {post_value} {post.currency}\n'
            elif 'narx' in prop[0].lower():
                text += f'\n<b>{prop[0]}</b>: {post_value} {post.currency}\n'
            else:
                text += f'\n<b>{prop[0]}</b>: {post_value}'

    # if post.longitude:
    #     markup = markups.get_geo(chat_id=publicator.id,
    #                              long=post.longitude,
    #                              lati=post.latitude)

    # if post.pictures:
    #     bot.send_media_group(chat_id=to_chat_id,
    #                          media=get_photos_from_db(post=post))

    # text += Tx \
    #     .get(chat_id=to_chat_id, text_id='keywords_prop') \
    #     .format(', '.join(word.word for word in post.keywords)) if post.keywords else ''

    publicator_text = Tx.get(chat_id=post.owner,
                             text_id='Publisher')
    text += '\n' + publicator_text.format(publicator.username)

    text += '\n\n\n' + Tx.get(chat_id=post.owner,
                              text_id='BotMessages.PostCheck.USUAL')
    pictures = []
    for picture_index, picture in enumerate(post.pictures):
        pictures.append(InputMediaPhoto(media=picture.image,
                                        caption=text if text and picture_index == 0 else '',
                                        parse_mode='html' if picture_index == 0 else None))

    return pictures


def output_posts(to_chat_id: int, posts: tuple, user_status: str):
    """
        Метод для вывода объявлений
    :param to_chat_id: кому выводить
    :param posts: какие объявления
    :param user_status: cтатус пользователя (кому выводится)
    :return:
    """
    global post

    for post in posts:
        global markup

        text, markup = '', None

        publicator: db_util.Users = post.owner

        props = get_product_props_with_names(post=post)

        for prop in props:
            type_, *other_args = prop[1].split('_')

            post_value = prop[2]

            if type_ in ('text', 'int', 'contact'):

                if 'цена' in prop[0].lower():
                    text += f'\n<b>{prop[0]}</b>: {post_value} {post.currency}\n'
                elif 'narx' in prop[0].lower():
                    text += f'\n<b>{prop[0]}</b>: {post_value} {post.currency}\n'
                else:
                    text += f'\n<b>{prop[0]}</b>: {post_value}'

        # if post.longitude:
        #     markup = markups.get_geo(chat_id=publicator.id,
        #                              long=post.longitude,
        #                              lati=post.latitude)

        # if post.pictures:
        #     bot.send_media_group(chat_id=to_chat_id,
        #                          media=get_photos_from_db(post=post))

        # text += Tx \
        #     .get(chat_id=to_chat_id, text_id='keywords_prop') \
        #     .format(', '.join(word.word for word in post.keywords)) if post.keywords else ''

        if user_status in db_util.Constants.STATUSES[3:]:
            text_to_moderator = Tx.get(chat_id=to_chat_id,
                                       text_id='BotMessages.PostCheck.MODERATE') \
                .format(publicator.username,
                        publicator.amount_warnings,
                        post.id)
            send_message(chat_id=to_chat_id,
                         text=text_to_moderator)

        post.views += 1
        post.save()

        publicator_text = Tx.get(chat_id=to_chat_id,
                                 text_id='Publisher')
        text += '\n' + publicator_text.format(publicator.username)

        text += '\n\n\n' + Tx.get(chat_id=to_chat_id,
                                  text_id='BotMessages.PostCheck.USUAL')

        if post.pictures:
            bot.send_media_group(chat_id=to_chat_id,
                                 media=get_photos_from_db(post=post))

        else:
            send_message(chat_id=to_chat_id,
                         text=text,
                         reply_markup=markup)

        time.sleep(Constants.Telegram.TIMEOUT_BEFORE_OUTPUT_MODERATE_POSTS)


def get_moderation_post_for_usual(chat_id: int):
    if posts := db_util.get_moderation_posts(chat_id=chat_id):
        output_posts(to_chat_id=chat_id,
                     posts=posts,
                     user_status=db_util.Constants.STATUSES[0])
        if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
            send_message(chat_id=chat_id,
                         text_id="BotMessages.Usual.POSTS_ON_MODERATE",
                         reply_markup=markups.post_menu(chat_id=chat_id))
    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.Usual.NOT_POST_ON_MODERATE",
                     reply_markup=markups.post_menu(chat_id=chat_id))


def get_active_post_for_usual(chat_id: int):
    if posts := db_util.get_active_posts(chat_id=chat_id):
        output_posts(to_chat_id=chat_id,
                     posts=posts,
                     user_status=db_util.Constants.STATUSES[0])

        if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
            send_message(chat_id=chat_id,
                         text_id="BotMessages.Usual.POSTED_POSTS",
                         reply_markup=markups.post_menu(chat_id=chat_id))

    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.Usual.NOT_ACTIVE_POSTS",
                     reply_markup=markups.post_menu(chat_id=chat_id))


def get_deleted_post_for_usual(chat_id: int):
    if posts := db_util.get_deleted_posts(chat_id=chat_id):
        output_posts(to_chat_id=chat_id,
                     posts=posts,
                     user_status=db_util.Constants.STATUSES[0])

        if db_util.get_user_status(chat_id=chat_id) != db_util.Constants.STATUSES[2]:
            send_message(chat_id=chat_id,
                         text_id="BotMessages.Usual.DELETED_POSTS",
                         reply_markup=markups.post_menu(chat_id=chat_id))
    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.Usual.NOT_DELETED_POSTS",
                     reply_markup=markups.post_menu(chat_id=chat_id))


def get_moderation_post_for_customer(chat_id: int, category_id: str):
    output_posts(to_chat_id=chat_id,
                 posts=db_util.get_post_by_category(category_id=category_id),
                 user_status=db_util.Constants.STATUSES[0])


def get_moderation_posts(chat_id: int):
    """

    :param chat_id: уникальный идентификатор пользователя
    :param get_moderation_post: метод для модератора и не только,
                                в котором можно управлять объявлением,
                                если обычный пользователь - None
    :return:
    """
    output_posts(to_chat_id=chat_id,
                 posts=db_util.get_moderation_posts(),
                 user_status=db_util.Constants.STATUSES[3])
    send_message(chat_id=chat_id,
                 text_id="BotMessages.PostCheck.GO_TO_EDIT",
                 reply_markup=markups.get_moderation_posts(chat_id=chat_id))


def send_new_post_to_channel(post_id: int):
    new_post = Post.get(Post.id == post_id)

    # переводим list из string в обычный list с помощью json
    selected_channels = json.loads(new_post.chosen_channels)

    for x in selected_channels:
        channel = Channel.get(Channel.id == int(x))
        if new_post.pictures:
            bot.send_media_group(chat_id=channel.channel_id, media=get_photos_from_db(post=new_post))

        else:
            text, markup = '', None

            publicator: db_util.Users = post.owner

            props = get_product_props_with_names(post=new_post)

            for prop in props:
                type_, *other_args = prop[1].split('_')

                post_value = prop[2]

                if type_ in ('text', 'int', 'contact'):

                    if 'цена' in prop[0].lower():
                        text += f'\n<b>{prop[0]}</b>: {post_value} {new_post.currency}\n'
                    elif 'narx' in prop[0].lower():
                        text += f'\n<b>{prop[0]}</b>: {post_value} {new_post.currency}\n'
                    else:
                        text += f'\n<b>{prop[0]}</b>: {post_value}'

            # if new_post.longitude:
            #     markup = markups.get_geo(chat_id=publicator.id,
            #                              long=new_post.longitude,
            #                              lati=new_post.latitude)

            markup = markups.reactions_to_post(counter=count)

            publicator_text = Tx.get(chat_id=new_post.owner,
                                     text_id='Publisher')
            text += '\n' + publicator_text.format(publicator.username)

            text += '\n\n\n' + Tx.get(chat_id=new_post.owner,
                                      text_id='BotMessages.PostCheck.USUAL')

            msg = bot.send_message(chat_id=channel.channel_id, text=text,
                                   reply_markup=markup)
            print(msg.id)
            time.sleep(10)
            bot.delete_message(chat_id=channel.channel_id, message_id=msg.id)
        channel.selected = False
        channel.save()

    else:
        print("Something went wrong when sending post to the channel")


def send_all_new_posts_to_channel():
    """
        Отправка всех объявлений в каналы
    """
    posts = Post.select().where(Post.moderate == True)

    for new_post in posts:

        if new_post.chosen_channels:
            send_new_post_to_channel(post_id=new_post.id)

        else:
            print("Something went wrong when sending post to the channel or no channels were chosen")
        time.sleep(.3)


@bot.callback_query_handler(func=lambda call: True)
def update_reactions_to_post(call):
    """
        Реакции пользователей на объявления
    """
    reactions = db_util.Reaction.select()

    for reaction in reactions:
        count = 0
        clicked = False
        if call.data == str(reaction.text):
            logger.info(f'User {call.message.chat.id} clicked on button {reaction.id}')
            if not clicked:
                count += 1
                clicked = True
            else:
                count -= 1
                clicked = False
            bot.edit_message_reply_markup(chat_id=call.message.id,
                                          reply_markup=markups.reactions_to_post(counter=count))
