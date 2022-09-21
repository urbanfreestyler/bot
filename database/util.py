from database.models import *
from database.services.session import SessionWork as session
from database.services.users import *
from database.services.posts import *
from database.services.cities import *
from database.services.posts import *
from database.services.categories import *
from database.services.multitexting import *
from database.services.settings import *
from database.services.statistic import *
from database.config import Constants


def create_tables():
    """
        Создание всех моделей
    :return:
    """
    Languages.create_table()
    BotMessages.create_table()
    Cities.create_table()
    Users.create_table()
    Categories.create_table()
    Pictures.create_table()
    logger.critical('Сделай в Picture поле image - LOBG BLOB!!!')
    Post.create_table()
    PostPictures.create_table()
    Settings.create_table()
    Statistic.create_table()

    KeyWord.create_table()
    PostKeywords.create_table()

    CategoriesMultiLang.create_table()

    Patterns.create_table()
    PatternProps.create_table()

    # Product.create_table()
    ProductProps.create_table()

    PatternsMultiLang.create_table()
    PatternsPropsMultilang.create_table()

    Channel.create_table()
    Transaction.create_table()

    Reaction.create_table()


if __name__ == '__main__':
    # print(StatisticWork.get_week())
    create_tables()
