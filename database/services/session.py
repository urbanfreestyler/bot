from database.models import Users


class SessionWork:
    """
        Класс для работы с сессией, взять установить значение
    """

    @staticmethod
    def get(chat_id: int, key: str):
        """
            Взять значение из сессии
        :param chat_id: айди пользователя
        :param key: ключ по которому лежит что-либо
        :return: значение под переданным ключом
        """
        return Users.get(Users.id == chat_id).session.get(key)

    @staticmethod
    def set(chat_id: int, key: str, value):
        """
            Установка нового значения в сесиию
        :param chat_id: айди пользователя
        :param key: ключ под которым будет новое значение
        :param value: новое значение
        :return:
        """
        user, created = Users.get_or_create(id=chat_id)
        session = user.session

        if '___' in key:
            # если в ключе есть ___ то делаем по ключу перед ___ словарь, в котором будет
            # ключ который расположен после ___, максимум один уровень вложенности
            key, dict_key = key.split('___')

            if session.get(key):
                session[key][dict_key] = value

            else:
                session[key] = {dict_key: value}

        else:
            session[key] = value

        user.save()

    @staticmethod
    def prepare_to_new_photo_load(chat_id: int):
        """
            Очистка данных из сессию пользователя,
            а именно данных о фотографиях которые он загружал ранее
        :param chat_id: айди пользователя
        :return:
        """
        user: Users = Users.get(Users.id == chat_id)
        if 'photo_number' in user.session:
            user.session.pop('photo_number')

        post_dict = user.session.get('post')
        for key in tuple(post_dict.keys()):
            if 'photo' in key:
                post_dict.pop(key)
        user.save()

    @staticmethod
    def set_next_and_prev_ids(chat_id: int, next: int, prev: int):
        SessionWork.set(chat_id=chat_id,
                        key='next',
                        value=next)
        SessionWork.set(chat_id=chat_id,
                        key='prev',
                        value=prev)

    @staticmethod
    def get_lang_code(chat_id: int) -> int:
        return SessionWork.get(chat_id=chat_id,
                               key='language')

    @staticmethod
    def update_key(chat_id: int, key: str, value, method: str):
        old_value = SessionWork.get(chat_id=chat_id,
                                    key=key)

        if method == 'append':

            if not isinstance(old_value, list):
                old_value = [value]
            else:
                old_value.append(value)

        elif method == 'update':

            if not isinstance(old_value, dict):
                old_value = value
            else:
                old_value.update(value)

        SessionWork.set(chat_id=chat_id,
                        key=key,
                        value=old_value)

    @staticmethod
    def start_add_post(chat_id: int):
        _ = SessionWork.set
        _(chat_id=chat_id, key='add_post', value=True)
        _(chat_id=chat_id, key='post', value={})
        _(chat_id=chat_id, key='price', value=False)
        _(chat_id=chat_id, key='post___currency', value='')
        _(chat_id=chat_id, key='post___pattern_id', value='')
        _(chat_id=chat_id, key='category_parent_id', value=None)
        _(chat_id=chat_id, key='selected_channels', value=None)
        _(chat_id=chat_id, key='post___geo',
          value={'longitude': None,
                 'latitude': None})
        _(chat_id=chat_id, key='continue', value='')

    @staticmethod
    def start_become_partner(chat_id: int):
        _ = SessionWork.set
        _(chat_id=chat_id, key='add_channel', value=True)
        _(chat_id=chat_id, key='channel', value={})
        _(chat_id=chat_id, key='channel_name', value='')
        _(chat_id=chat_id, key='channel_username', value='')
        _(chat_id=chat_id, key='channel_id', value='')
        _(chat_id=chat_id, key='channel___pattern_id', value=None)
        _(chat_id=chat_id, key='price_for_post', value=None)

    @staticmethod
    def pop(chat_id: int, key: str):
        # data = SessionWork.get(chat_id=chat_id,
        #                        key=key)
        user = Users.get(id=chat_id)
        session = user.session
        data = session.pop(key)
        user.save()

        return data
