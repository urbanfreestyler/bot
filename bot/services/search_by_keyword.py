from bot.util import *


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.SearchByKeyWords"))
@bot.message_handler(commands=Commands.SEARCH)
def get_keyword_to_search(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text_id='get_keywords',
                 method=search_posts_by_keywords)


def search_posts_by_keywords(message: Message):
    from bot.services.search_post import get_next_direction_on_search

    chat_id, text, message_id = get_info_from_message(message=message)
    keywords = list(word.strip().lower() for word in text.split(','))
    posts = db_util_post.get_posts_by_keywords(keywords=keywords)
    if not posts:
        send_message(chat_id=chat_id,
                     text_id='no_founded_posts',
                     reply_markup=markups.main_menu(chat_id=chat_id))
    else:
        get_next_direction_on_search(chat_id=chat_id,
                                     post=posts[0])


