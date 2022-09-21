from database.models import Settings


def get_setting(setting_id: int = 0, setting_title: str = '') -> str:
    """
        Получение какой-либо настройки из базы
    :param setting_id: айди настройки
    :param setting_title: название настроки
    :return: значение настройки
    """
    if setting_id:
        return Settings.get_by_id(setting_id).value

    else:
        return Settings.get(Settings.title == setting_title).value


def get_settings_list() -> tuple[Settings]:
    return Settings.select()

def set_setting(setting_id: str, value: str):
    settings = Settings.get(Settings.id == setting_id)
    settings.value = value
    settings.save()
