import datetime
from database.config import Constants
from database.models import Users
from database.services.session import SessionWork as session
from database.services.settings import get_setting


def get_user_status(chat_id: int) -> str:
    return Users.get(Users.id == chat_id).status


def add_user_city(chat_id: int, city_id: int):
    user: Users = Users.get(Users.id == chat_id)
    user.city = city_id
    user.save()


def add_phone_to_user(chat_id: int, phone: str):
    user = Users.get(Users.id == chat_id)
    user.phone = phone
    user.save()


def get_users_list(status: str):
    if status == Constants.STATUSES[3]:
        statuses = Constants.STATUSES[:3]

    elif status == Constants.STATUSES[4]:
        statuses = Constants.STATUSES[:4]

    else:
        statuses = Constants.STATUSES[:]

    return tuple(Users
                 .select(Users.id,
                         Users.username,
                         Users.first_name,
                         Users.status)
                 .where(Users.status in statuses)
                 .tuples())


def get_user_data(user_id: str) -> Users:
    """
        Получение пользователя и его данных из бд в виде объекта
    :param user_id: айди пользователя
    :return: объект users
    """
    return Users.get(Users.id == user_id)


def block_user(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[2]
    amount_blocked_days = int(get_setting(setting_id=Constants.Settings.DAYS_ON_BLOCK))
    user.expire_status_date = datetime.datetime.now() + datetime.timedelta(days=amount_blocked_days)
    user.save()
    return user.id, user.username, amount_blocked_days, user.expire_status_date


def unblock_user(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[0]
    user.save()
    return user_id, user.username


def provide_vip(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[1]
    amount_vip_days = int(get_setting(setting_id=Constants.Settings.DAYS_ON_VIP))
    user.expire_status_date = datetime.datetime.now() + datetime.timedelta(days=amount_vip_days)
    user.save()
    return user.id, user.username, amount_vip_days, user.expire_status_date


def remove_vip(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[0]
    user.save()
    return user.id, user.username


def provide_moder(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[3]
    user.save()
    return user.id, user.username


def provide_admin(user_id: str) -> tuple:
    user: Users = Users.get(Users.id == user_id)
    user.status = Constants.STATUSES[4]
    user.save()
    return user.id, user.username


def get_expire_date(user_id: int) -> datetime.datetime:
    return Users.get(Users.id == user_id).expire_status_date


def refresh_status():
    Users \
        .update({Users.status: Constants.STATUSES[0],
                 Users.expire_status_date: None}) \
        .where((Users.status.in_(Constants.STATUSES[1:3])) &
               (Users.expire_status_date < datetime.datetime.now())).execute()


class UserWork:
    @staticmethod
    def add(**user_data):
        chat_id = user_data['id']

        language = session.get(chat_id=chat_id,
                               key='language')

        Users.delete_by_id(chat_id)

        Users(**user_data).save(force_insert=True)

        session.set(chat_id=chat_id,
                    key='language',
                    value=language)

    @staticmethod
    def get_phone(chat_id: int) -> str:
        return Users.get(Users.id == chat_id).phone

    @staticmethod
    def get_all_amount() -> int:
        return Users.filter().count()


def get_users_list_with_nick(contains: str):
    return tuple(Users
                 .select(Users.id,
                         Users.username,
                         Users.first_name,
                         Users.status)
                 .filter(Users.username.contains(contains))
                 .tuples())

