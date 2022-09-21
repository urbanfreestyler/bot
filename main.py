from daemon_support.daemon_sup import main_cycle, save_activities
from database.util import create_tables, get_category_parents_ids
from bot.util import start_bot_from_code
from bot.websocket import start_server
from threading import Thread
from time import sleep

if __name__ == '__main__':
    # create_tables()
    # sleep(2)
    Thread(target=main_cycle, daemon=True).start()
    Thread(target=save_activities, daemon=True).start()
    start_bot_from_code()
    # start_server()
