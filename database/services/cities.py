from database.models import Cities


def get_cities() -> tuple[Cities]:
    return Cities.select()
