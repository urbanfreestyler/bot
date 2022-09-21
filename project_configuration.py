import functools
import os

from telebot.types import Message


def create_virtualenv():
    """
        Создание виртуальной среды для запуска всего кода
    :return:
    """
    try:
        import loguru

    except ModuleNotFoundError:

        separator = '\n' + '=' * 100 + '\n'
        print(separator + '\nVenv not setup, creating venv...\n' + separator)
        os.system('python -m venv venv')

        activate_this = 'venv/Scripts/activate_this.py'
        with open(activate_this) as f:
            code = compile(f.read(), activate_this, 'exec')
            exec(code, dict(__file__=activate_this))

        print(separator + '\nInstall requirements...\n' + separator)
        os.system('pip install -r requirements.txt')

        from loguru import logger
        print('\n\n')
        logger.success('Установка и настройка venv успешно завершена.')


# create_virtualenv()


from loguru import logger
import daemon_support.temp_storage as temp_stor


# установка настроек логгера
logger.add('logs.txt')


def logging(*, entry=True, exit=True, level="DEBUG"):

    def wrapper(func):
        name = func.__name__

        @functools.wraps(func)
        def wrapped(*args, **kwargs):
            logger_ = logger.opt(depth=1)
            if entry:
                # logger_.log(level, "Entering '{}' (args={}, kwargs={})", name, args, kwargs)
                logger_.log(level, "Entering '{}'", name)

            if args and isinstance(args[0], Message):
                temp_stor.new_user(chat_id=args[0].from_user.id)

            result = func(*args, **kwargs)
            # if exit:
            #     logger_.log(level, "Exiting '{}' (result={})", name, result)
            return result

        return wrapped

    return wrapper


class Constants:
    """
        Класс для установки констант
    """
    pass

