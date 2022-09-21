import datetime
from time import sleep
import database.util as db_util
from daemon_support.config import Constants, logger
import daemon_support.temp_storage as temp_stor


def save_activities():
    logger.info('Start activities threads')
    today = datetime.date.today()
    while True:
        if today != datetime.date.today():

            amount_players = temp_stor.get_amount_players()

            db_util.StatisticWork.set_new_day(amount_users=amount_players)

            temp_stor.remove_users_list()

            today = datetime.date.today()
            logger.success(f'Write today activity. {datetime.date.today()} / {amount_players}')
        sleep(60)


def main_cycle():
    logger.info('Start clear statuses thread.')
    while True:
        db_util.refresh_status()
        logger.success('Clear statuses success')
        sleep(Constants.PERIOD)

