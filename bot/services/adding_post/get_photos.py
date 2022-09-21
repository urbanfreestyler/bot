from threading import Thread
from time import sleep

from telebot.types import InputMediaPhoto

from bot.util import *

for_photos = {}

callback_to_back_question = callback_to_exit = None


def get_pictures(chat_id: int, callback_to_next, callback_to_back):
    global callback_to_exit, callback_to_back_question

    callback_to_exit = callback_to_next
    callback_to_back_question = callback_to_back

    session.prepare_to_new_photo_load(chat_id=chat_id)
    session.set(chat_id=chat_id,
                key='upload_photos_status',
                value=True)
    session.set(chat_id=chat_id,
                key='photos_for_post',
                value=[])
    for_photos[chat_id] = []

    get_photo_request(chat_id=chat_id)

    Thread(target=get_first_photo,
           args=(chat_id,), ).start()


def get_photo_request(chat_id: int, error: bool = False):
    send_message(chat_id=chat_id,
                 text_id='BotMessages.AddPost.ERROR_GET_PICTURES' if error else 'BotMessages.AddPost.GET_PICTURES',
                 reply_markup=markups._reply_markup(chat_id=chat_id,
                                                    back_=True,
                                                    skip=True),
                 method=skip_photo, )


def skip_photo(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if message.content_type == 'photo':
        set_pictures(message=message)

    elif text == Tx.get(chat_id=chat_id,
                        text_id='skip'):
        callback_to_exit(chat_id=chat_id)

    elif text == Tx.get(chat_id=chat_id,
                        text_id='Buttons.Direction.BACK'):
        callback_to_back_question(chat_id=chat_id, back=True)

    else:
        get_photo_request(chat_id=chat_id,
                          error=True)


def download_file(file_id) -> str:
    photo = bot.get_file(file_id)
    filename = Constants.Paths.TEMP_PHOTOS + photo.file_path.split('/')[-1]
    with open(filename, 'wb') as file:
        file.write(bot.download_file(file_path=photo.file_path))
    return filename


@bot.message_handler(content_types=['photo'])
def set_pictures(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)
    if session.get(chat_id=message.from_user.id,
                   key='upload_photos_status'):
        for_photos[chat_id].append(download_file(file_id=message.photo[-1].file_id))


def get_first_photo(chat_id: int):
    amount_second_after_first_load = 0
    amount_second_to_die = 0  # кол-во секунд после который поток умрет

    while True:
        sleep(1)

        if amount_second_after_first_load > 5:
            break

        if len(for_photos[chat_id]):
            if amount_second_after_first_load == 0:
                send_message(chat_id=chat_id,
                             text_id='handle_photos',
                             reply_markup=markups.ReplyKeyboardRemove())
                amount_second_to_die = -100
            amount_second_after_first_load += 1

        amount_second_to_die += 1

        if amount_second_to_die == 30:
            session.set(chat_id=chat_id,
                        key='upload_photos_status',
                        value=False)
            return

    photos = for_photos[chat_id][:int(session.get(chat_id=chat_id,
                                                  key='current_question')[1].split('_')[1])]
    for_photos[chat_id] = photos

    photos_for_send = []

    for photo in photos:
        with open(photo, 'rb') as file:
            photos_for_send.append(InputMediaPhoto(media=file.read()))

    if len(photos) > 1:
        bot.send_media_group(chat_id=chat_id,
                             media=photos_for_send),
        get_first_photo_index(chat_id=chat_id)

    else:
        set_photo(chat_id=chat_id,
                  photo_number='1')


def get_first_photo_index(chat_id: int, error: bool = False):
    if not error:
        text = Tx.get(chat_id=chat_id,
                      text_id='first_photo')
    else:
        text = Tx.get(chat_id=chat_id,
                      text_id='Enter number from 1')

    send_message(chat_id=chat_id,
                 text=text.format(len(for_photos[chat_id])),
                 reply_markup=markups.back(chat_id=chat_id),
                 method=set_first_photo)


def set_first_photo(message: Message):
    chat_id, text, message_id = get_info_from_message(message=message)

    if text == Tx.get(chat_id=message.from_user.id, text_id="Buttons.Direction.BACK"):
        callback_to_back_question(chat_id=chat_id, back=True)

    elif text and text.isdigit() and 1 <= int(text) <= len(for_photos[chat_id]):
        set_photo(chat_id=chat_id,
                  photo_number=text)

    else:
        get_first_photo_index(chat_id=chat_id,
                              error=True)


def set_photo(chat_id: int, photo_number: str):
    photos_list = for_photos[chat_id]
    photo_index = int(photo_number) - 1
    photos_list[photo_index], photos_list[0] = photos_list[0], photos_list[photo_index]
    session.set(chat_id=chat_id,
                key='post___photos',
                value=photos_list)
    session.set(chat_id=chat_id,
                key='upload_photos_status',
                value=False)
    for_photos[chat_id].clear()
    callback_to_exit(chat_id=chat_id)
