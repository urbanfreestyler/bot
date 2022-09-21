from bot.general_controllers import start_bot
from bot.util import *


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Moderator.WORK_WITH_USERS") and
                                          db_util.get_user_status(
                                              chat_id=message.from_user.id) in db_util.Constants.STATUSES[3:])
def manipulate_with_users(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} start edit user')
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Moderator.MANIPULATE_WITH_USERS",
                 reply_markup=markups.users(chat_id=chat_id),
                 method=search_user
                 )


# Удаленме постов (тест)
@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Moderator.WORK_WITH_POSTS") and
                                          db_util.get_user_status(
                                              chat_id=message.from_user.id) in db_util.Constants.STATUSES[3:])
def manipulate_with_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} start edit post')
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Moderator.MANIPULATE_WITH_POSTS",
                 reply_markup=markups.posts(chat_id=chat_id),
                 method=search_post
                 )


@bot.message_handler(func=lambda message: message.text == Tx.get(chat_id=message.from_user.id,
                                                                 text_id="Buttons.Menu.Post.Delete"))
def manipulate_with_own_posts(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    logger.info(f'User {chat_id} start edit own post')

    if not db_util.Post.select().where((db_util.Post.owner==chat_id) & (db_util.Post.active==True)):
        send_message(chat_id=chat_id,
                     text=Tx.get(chat_id=chat_id,
                                 text_id='BotMessages.Usual.NOTHING_TO_DELETE'))

    else:
        send_message(chat_id=chat_id,
                     text_id="BotMessages.Moderator.MANIPULATE_WITH_POSTS",
                     reply_markup=markups.own_posts(chat_id=chat_id),
                     method=search_own_post
                     )


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.USERS_CHANGER[:-2]))
def change_users(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.USERS_CHANGER)

    if text[text.rfind('__') + 2:] == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        start_bot(message=message)

    elif '__' in text:
        # если пролистывает человек
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=markups.users(offset=int(text[text.rfind('__') + 2:]),
                                                                 chat_id=chat_id))

    else:
        status, user_id = text.split('_')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)

        user = db_util.get_user_data(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.WHAT_YOU_WANNA_DO")
                         .format(user.username,
                                 user.phone,
                                 user.amount_posts,
                                 user.amount_warnings,
                                 Constants.Telegram.STATUSES_TITLES[user.status],
                                 (f': до <u>{user.expire_status_date}</u>') if user.status in
                                                                               db_util.Constants.STATUSES[
                                                                               1:3] else '', ),
                         reply_markup=markups.user_edit_menu(status=status,
                                                             user_id=user_id))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.USER_EDIT[:2]))
def change_user(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.USER_EDIT)
    operation, user_id = text.split('__')
    logger.info(f'User {chat_id} edit user with operation')

    if operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.BLOCK_USER"):
        user_id, username, amount_vip_days, expire_date = db_util.block_user(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.USER_WAS_BLOCKED")
                         .format(username,
                                 amount_vip_days,
                                 expire_date))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Blocked.YOU_WERE_BLOCKED")
                         .format(amount_vip_days,
                                 expire_date))

    if operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.UNBLOCK_USER"):
        user_id, username = db_util.unblock_user(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.USER_WAS_UNBLOCKED")
                         .format(username, ))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Blocked.YOU_WERE_UNBLOCKED"))

    elif operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.PROVIDE_VIP"):
        user_id, username, amount_vip_days, expire_date = db_util.provide_vip(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.USER_WAS_VIPED")
                         .format(username,
                                 amount_vip_days,
                                 expire_date))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.YOU_BEEN_PROVIDED_VIP")
                         .format(amount_vip_days,
                                 expire_date,
                                 db_util.get_setting(setting_id=db_util
                                                     .Constants
                                                     .Settings
                                                     .AMOUNT_POSTS_FOR_VIP)))

    elif operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.REMOVE_VIP"):
        user_id, username = db_util.remove_vip(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.VIP_WAS_REMOVED")
                         .format(username, ))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Vip.YOUR_VIP_WAS_REMOVED"))

    elif operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.PROVIDE_MODERATION"):
        user_id, username = db_util.provide_moder(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Admin.USER_WAS_MODERATED").format(username))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.YOU_BEEN_PROVIDED_MODER"))

    elif operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.UserEdit.PROVIDE_ADMIN"):
        user_id, username = db_util.provide_admin(user_id=user_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Admin.USER_WAS_ADMIN").format(username))
        bot.send_message(chat_id=user_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.YOU_BEEN_PROVIDED_ADMIN"))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.POSTS_CHANGER[:-2]))
def change_posts(message: Message):
    global post_id
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.POSTS_CHANGER)
    if text[text.rfind('__') + 2:] == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        start_bot(message=message)

    elif '__' in text:
        # если пролистывает человек
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=markups.posts(offset=int(text[text.rfind('__') + 2:]),
                                                                 chat_id=chat_id))
    else:
        status, post_id = text.split('_')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)

        post = db_util.get_post_data(id=post_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.POST_INFO")
                         .format(post.id,
                                 post.owner_id,
                                 post.city_id),

                         reply_markup=markups.post_edit_menu(status=status,
                                                             user_id=str(chat_id)))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.POST_DELETE[:2]))
def change_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.POST_DELETE)

    operation, admin_id = text.split('__')

    logger.info(f'User {chat_id} edit post with operation')
    if operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.PostEdit.DELETE_POST"):
        postId = db_util.post_delete(post_id=post_id)  # <-- исправить

        post = db_util.get_post_data(id=postId)
        post_owner = post.owner_id

        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.POST_WAS_DELETED")
                         .format(post, ))

        bot.send_message(chat_id=post_owner,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.YOUR_POST_WAS_DELETED")
                         .format(post, ))


def search_user(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Moderator.MANIPULATE_WITH_USERS",
                 reply_markup=markups.users(chat_id=chat_id,
                                            contains=text),
                 method=search_user)


def search_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Moderator.MANIPULATE_WITH_POSTS",
                 reply_markup=markups.posts(chat_id=chat_id,
                                            contains=text),
                 method=search_post)


def search_own_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    send_message(chat_id=chat_id,
                 text_id="BotMessages.Moderator.MANIPULATE_WITH_POSTS",
                 reply_markup=markups.own_posts(chat_id=chat_id,
                                                contains=text),
                 method=search_own_post)


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.OWN_POSTS_CHANGER[:-2]))
def change_user_posts(message: Message):
    global post_id
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.OWN_POSTS_CHANGER)
    if text[text.rfind('__') + 2:] == 'back':
        delete_message(chat_id=chat_id,
                       message_id=message_id)
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)
        start_bot(message=message)

    elif '__' in text:
        # если пролистывает человек
        bot.edit_message_reply_markup(chat_id=chat_id,
                                      message_id=message_id,
                                      reply_markup=markups.own_posts(offset=int(text[text.rfind('__') + 2:]),
                                                                     chat_id=chat_id))
    else:
        status, post_id = text.split('_')
        bot.clear_step_handler_by_chat_id(chat_id=chat_id)

        post = db_util.Post.get(db_util.Post.id == post_id)
        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Moderator.POST_INFO")
                         .format(post.id,
                                 post.owner_id,
                                 post.city_id),

                         reply_markup=markups.own_post_edit_menu(status=status,
                                                                 user_id=str(chat_id)))


@bot.callback_query_handler(func=lambda message: message.data.startswith(Callbacks.OWN_POST_DELETE[:2]))
def change_user_post(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message,
                                                      callback_str=Callbacks.OWN_POST_DELETE)

    operation, chat_id = text.split('__')

    logger.info(f'User {chat_id} user edit post with operation')
    if operation == Tx.get(chat_id=message.from_user.id, text_id="Buttons.PostEdit.DELETE_POST"):
        post = db_util.get_users_posts(owner_id=chat_id)

        bot.send_message(chat_id=chat_id,
                         text=Tx.get(chat_id=chat_id, text_id="BotMessages.Usual.YOUR_POST_WAS_DELETED")
                         .format(post, ))
