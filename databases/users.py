import json
import logging
import os
from variables import GLOBAL_LOGGER_LEVEL, PATH_TO_USERS_DATA_BASE

logger = logging.getLogger('users_db')
logger.setLevel(GLOBAL_LOGGER_LEVEL)
db = {}
location = ''


def load():
    """
    Считывает файл базы данных и загружает ее в переменную
    :return: None
    """

    global logger, db, location

    logger.debug('Загрузка бд пользователей')

    location = os.path.expanduser(PATH_TO_USERS_DATA_BASE)

    if os.path.exists(location):
        db = json.load(open(location, 'r'))


def _check_user(user_id: int):
    """
    Проверяет существование id пользователя в базе данных
    :param user_id: id пользователя, которого надо проверить
    :return: True - если id есть в базе данных, False - если нет
    """

    global logger, db

    logger.debug(f'Проверка существования пользователя. id:{user_id}')
    return str(user_id) in db.keys()


def _dump_db():
    """
    Сохраняет базу данных в текстовый файл.
    :return: None
    """
    try:
        logger.debug('Сохранение дб')

        json.dump(db, open(location, 'w+'))
        logger.debug('Бд сохранена')
    except Exception as e:
        logger.error('Не удалось сохранить бд', e)


def add_user(user_id: int):
    """
    Добавляет id пользователя в базу данных
    :param user_id: id пользователя
    :return: None
    """

    global logger, db

    try:
        logger.debug(f'Добавление пользователя. id:{user_id}')

        if _check_user(user_id):
            logger.debug(f'Пользователь уже добавлен. id:{user_id}')
            return

        db[str(user_id)] = {}
        _dump_db()
        logger.debug(f'Пользователь создан. id:{user_id}')
    except Exception as e:
        logger.error(f'Не удалось сохранить пользователя. id:{user_id}', e)


def get_datas(user_id: int, category: str):
    """
    Возвращает список в формате {'Год': {'Месяц (число)', 'Расход'}, и т.д.}
    :param user_id: id пользователя, у которого надо взять расходы
    :param category: категория, по которой ищутся расходы
    :return: Список расходов
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Запрос всех показаний пользователя по категории. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не добавлен. {debug_text}')
            add_user(user_id)

        if category not in db[str(user_id)]:
            logger.debug(f'Категория не существует. {debug_text}')
            return {}
        return db[str(user_id)][category]
    except Exception as e:
        logger.error(f'Не удалось отправить все показания. {debug_text}', e)
        return {}


def get_categories_name(user_id: int):
    """
    Возвращаяет название категорий пользователя
    :param user_id: id пользователя
    :return: массив в формате ['Название', и тд]
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Запрос всех названий категорий. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. {debug_text}')
            add_user(user_id)

        return list(db[str(user_id)].keys())
    except Exception as e:
        logger.error(f'Не удалось категории пользователя. {debug_text}', e)
        return {}


def check_category(user_id: int, category: str):
    """
    Возвращаяет существует ли категория у пользлователя
    :param user_id: id пользователя
    :param category: категория, которую необходимо проверить
    :return: True - существет категория, False - если нет
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Запрос всех названий категорий. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. {debug_text}')
            add_user(user_id)
            return False

        return category in db[str(user_id)].keys()
    except Exception as e:
        logger.error(f'Не удалось категории пользователя. {debug_text}', e)
        return {}


def check_year(user_id: int, category: str, year: str):
    """
    Возвращаяет существует ли год в определённой категории у пользлователя
    :param user_id: id пользователя
    :param category: категория, где нужно проверить год
    :param year: год, который необходимо проверить
    :return: True - существет категория, False - если нет
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Запрос всех названий категорий. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. {debug_text}')
            add_user(user_id)
            return False

        if not check_category(user_id, category):
            return False
        return year in db[str(user_id)][category]
    except Exception as e:
        logger.error(f'Не удалось категории пользователя. {debug_text}', e)
        return {}


def add_category(user_id: int, category_name: str):
    """
    Добавляет категорию пользователя
    :param user_id: id пользователя
    :param category_name: название новой категории
    :return: None
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Добавление категории. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. {debug_text}')
            add_user(user_id)

        if category_name in db[str(user_id)]:
            logger.error(f'Категория уже существует. {debug_text}')
            return

        db[str(user_id)][category_name] = {}
        _dump_db()
        logger.debug(f'Добавление категории завершено. {debug_text}')
    except Exception as e:
        logger.error(f'Не удалось сохранить категорию. {debug_text}', e)


def add_data(user_id: int, category: str, year: str, month: str, data: str) -> int:
    """
    Добавляет расход пользователя
    :param user_id: id пользователя
    :param category: категория
    :param year: год
    :param month: месяц
    :param data: расход
    :return: 0 - произошла ошибка, 1 - показания добавлены, 2 - показания изменены
    """

    global logger, db

    debug_text = f'id:{user_id}'

    try:
        logger.debug(f'Сохранение расхода. {debug_text}')

        if data[-1] in [',', '.']:
            data = data[0:len(data) - 1]

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. {debug_text}')
            add_user(user_id)

        if not (category in db[str(user_id)]):
            logger.error(f'Категория не найдена. {debug_text}')
            add_category(user_id, category)

        if year not in db[str(user_id)][category]:
            db[str(user_id)][category][year] = {}

        if month not in db[str(user_id)][category][year]:
            db[str(user_id)][category][year][month] = data
            logger.debug(f'Сохранение завершено. {debug_text}')
            _dump_db()
            return 1
        else:
            db[str(user_id)][category][year][month] = data
            logger.debug(f'Расход уже сохранен за этот период. Данные обновлены. {debug_text}')
            _dump_db()
            return 2
    except Exception as e:
        logger.error(f'Не удалось добавить расход. {debug_text}', e)
        return 0
