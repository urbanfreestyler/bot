from database.util import *


class Validator:
    """
        Класс для валидации данных
    """

    @staticmethod
    def exist_user(chat_id: int) -> bool:
        return Users.select().where(Users.id == chat_id).exists()

    @staticmethod
    def user_phone(chat_id: int) -> str:
        return Users.get(Users.id == chat_id).phone

    @staticmethod
    def check_price(value: str) -> bool:
        return len(value) <= int(get_setting(setting_id=Constants.Settings.PRICE_AMOUNT_NUMBERS))

    # !!!!!!!!!!!!!!!!!!!!
    # не забудь про статус
    # !!!!!!!!!!!!!!!!!!!!

    @staticmethod
    def check_available_posts(chat_id: int) -> bool:
        user: Users = Users.get(Users.id == chat_id)

        if user.refresh_date != datetime.date.today():
            user.available_posts = get_setting(setting_id=Constants.Settings.AMOUNT_POSTS_FOR_USUAL if user.status == Constants.STATUSES[0] else Constants.Settings.AMOUNT_POSTS_FOR_VIP)
            user.refresh_date = datetime.date.today()

        return bool(user.available_posts)

    @staticmethod
    def post_exists(value: str) -> bool:
        return Post.get_or_none(Post.id == value)
