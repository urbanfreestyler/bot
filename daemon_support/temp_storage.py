# import redis
#
# redis = redis.Redis(
#     host='localhost',
#     port='6379'
# )

from redis import Redis
#
#
SetNameUsers = 'users'
#
#
class TempStorage:
    _redis: Redis

    def __init__(self):
        self._redis = Redis(host='localhost')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._redis.close()

    def new_user(self, chat_id: int):
        self._redis.sadd(SetNameUsers, chat_id)

    def get_users(self):
        return self._redis.scard(SetNameUsers)

    def clear_users(self):
        self._redis.delete(SetNameUsers)


def new_user(chat_id: int):
    with TempStorage() as ts:
        ts.new_user(chat_id=chat_id)


def get_amount_players():
    with TempStorage() as ts:
        return ts.get_users()


def remove_users_list():
    with TempStorage() as ts:
        return ts.clear_users()
