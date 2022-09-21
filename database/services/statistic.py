import datetime

from loguru import logger
from peewee import fn

from database.models import Statistic


class StatisticWork:
    """
        Работ с статистикой
    """
    @staticmethod
    def set_new_day(amount_users: int):
        try:
            Statistic(amount_users=amount_users).save(force_insert=True)
        except Exception as e:
            logger.exception('Error in set_new_day')

    @staticmethod
    def get_week() -> int:
        row = tuple(Statistic
                    .select(fn.SUM(Statistic.amount_users))
                    .where(Statistic.view_date.between(datetime.date.today() - datetime.timedelta(days=7),
                                                       datetime.date.today()))
                    .tuples())
        return row[0][0]

    @staticmethod
    def get_month():
        row = tuple(Statistic
                    .select(fn.SUM(Statistic.amount_users))
                    .where(Statistic.view_date.between(datetime.date.today() - datetime.timedelta(days=30),
                                                       datetime.date.today()))
                    .tuples()
                    )
        return row[0][0]
