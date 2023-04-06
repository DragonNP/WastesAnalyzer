import json
import logging
import os
from databases import db_messages
from variables import GLOBAL_LOGGER_LEVEL, PATH_TO_RESULT_POLL_DATA_BASE

logger = logging.getLogger('polls_counters')
logger.setLevel(GLOBAL_LOGGER_LEVEL)
counters = {}
db = {}
location = ''


def load():
    """
    Считывает файл базы данных и загружает ее в переменную
    :return: None
    """

    global logger, db, location

    logger.debug('Загрузка бд результатов опроса')

    location = os.path.expanduser(PATH_TO_RESULT_POLL_DATA_BASE)

    if os.path.exists(location):
        db = json.load(open(location, 'r'))

    if db == {}:
        for key in db_messages.Poll.options:
            db[key] = 0
        _dump_db()


def update_counter(user_id: int):
    """
    Обновляет счетчик отправленных сообщений, если счетчик > 15, отправить опрос
    :param user_id: id пользователя
    :return: Всегда True
    """
    logger.debug(f'Обновляем счетчик. id:{user_id}')

    if user_id in counters:
        counters[user_id] += 1
    else:
        counters[user_id] = 1
    if counters[user_id] > 15:
        counters[user_id] = 0
    return True


def check_send_poll(user_id: id):
    """
    Проверка на необходимость отправки опроса
    :param user_id: id пользователя
    :return: True - если надо отправить опрос, False - если нет
    """
    logger.debug(f'Проверяем счетчик. id:{user_id}')

    if user_id not in counters:
        counters[user_id] = 1
        return False
    if counters[user_id] == 0:
        counters[user_id] = 1
        return True


def save_result(answer: str):
    db[answer] += 1
    _dump_db()


def _dump_db():
    """
    Сохраняет базу данных в текстовый файл.
    :return: None
    """

    global logger, db, location

    try:
        logger.debug('Сохранение дб')

        json.dump(db, open(location, 'w+'))
        logger.debug('Бд сохранена')
    except Exception as e:
        logger.error('Не удалось сохранить бд', e)
