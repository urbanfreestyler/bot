from project_configuration import *


class Constants(Constants):
    # DB_CONNECTION_PARAMS = {'user': 'root',
    #                         'password': 'root',
    #                         'database': 'bot_announcement',
    #                         'charset': 'utf8mb4',
    #                         'host': 'db',
    #                         }
    DB_CONNECTION_PARAMS = {'user': 'root',
                            'password': 'isbn9789943',
                            'database': 'bot_announcement',
                            'charset': 'utf8mb4',
                            'host': 'localhost',
                            }

    STATUSES = ('usual',
                'vip',
                'blocked',
                'moderator',
                'admin',
                'mainadmin',)

    LIMIT_CATEGORIES = 20
    LIMIT_USERS = 15
    LIMIT_POSTS = 15
    AMOUNT_POSTS_TO_CUS = 10

    class Length:
        """
            длины чего-либо
        """
        STATUS = 16

        class Telegram:
            """
                длинны для телеграмма
            """
            USERNAME = 32
            FIRST_NAME = 64
            PHONE = 16

        class Settings:
            """
                длинны для настроек по части логики
            """
            TITLE = 64
            VALUE = 64
            ENDINGS = 16

    class Settings:
        AMOUNT_SYMBOLS_IN_DESCRIPTION = 1
        AMOUNT_PICTURES = 2
        PICTURE_SIZE = 3
        MODERATE_STATUS = 4
        PRICE_AMOUNT_NUMBERS = 5
        AMOUNT_POSTS_FOR_USUAL = 6
        AMOUNT_POSTS_FOR_VIP = 7
        AMOUNT_SYMBOLS_IN_TITLE = 8
        DAYS_ON_BLOCK = 9
        DAYS_ON_VIP = 10

