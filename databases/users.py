import json
from variables import *

logger = logging.getLogger('users_db')
db_loaded = False
db = {}
location = ''


def load():
    global logger, db_loaded, db, location

    logger.setLevel(GLOBAL_LOGGER_LEVEL)
    logger.debug('Начало загрузки бд пользователей')

    location = os.path.expanduser(PATH_TO_USERS_DATA_BASE)

    if os.path.exists(location):
        db = json.load(open(location, 'r'))

    db_loaded = True
    logger.debug('Загрузка бд пользователей завершена')


def _check_db_loaded():
    global logger, db_loaded

    logger.debug('Проверка загрузки бд')

    if not db_loaded:
        load()


def _check_user(user_id: int):
    global logger, db

    logger.debug('Проверка существования пользователя')
    _check_db_loaded()
    return str(user_id) in db.keys()


def _dump_db():
    global logger, db, location

    try:
        logger.debug('Сохранение дб')

        _check_db_loaded()

        json.dump(db, open(location, 'w+'))
        logger.debug('Бд сохранена')
    except Exception as e:
        logger.error('Не удалось сохранить бд', e)


def add_user(user_id: int):
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
    global logger, db

    debug_text = f'id:{user_id} категория:{category}'

    try:
        logger.debug(f'Запрос всех показаний пользователя по категории. {debug_text}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не добавлен. {debug_text}')
            add_user(user_id)

        if category not in db[str(user_id)]:
            logger.debug(f'Категория не существует. {debug_text}')
            return {}

        logger.debug(f'Запрос отправлен. {debug_text}')
        return db[str(user_id)][category]
    except Exception as e:
        logger.error(f'Не удалось отправить все показания. {debug_text}', e)
        return {}


def get_categories_name(user_id: int):
    global logger, db

    try:
        logger.debug(f'Запрос всех названий категорий. id:{user_id}')

        if not _check_user(user_id):
            logger.debug(f'Пользователь не найден. id:{user_id}')
            add_user(user_id)

        logger.debug(f'Запрос отправлен. id:{user_id}')
        return list(db[str(user_id)].keys())
    except Exception as e:
        logger.error(f'Не удалось категории пользователя. id:{user_id}', e)
        return {}


def add_category(user_id: int, category_name: str):
    global logger, db
    debug_text = f'id:{user_id}, имя:{category_name}'

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


def add_data(user_id: int, category: str, year: str, month: str, data: str):
    global logger, db
    debug_text = f'id:{user_id}, год:{year}, месяц:{month}, данные:{data}'

    try:
        logger.debug(f'Сохранение показания. {debug_text}')

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
            _dump_db()
            logger.debug(f'Сохранение завершено. {debug_text}')
        else:
            logger.error(f'Показания уже сохранены за этот период. {debug_text}')
    except Exception as e:
        logger.error(f'Категория не найдена. Не удалось добавить показания {debug_text}', e)

# def check_link(self, str(user_id): int, name: str):
#     res = name in self.db[str(str(user_id))]
#     self.logger.debug(f'Проверка ссылки в базе данных. результат:{res}')
#     return res

# def remove_link(self, str(user_id): int, name: str):
#     self.logger.debug(f'Удаление ссылки. id пользователя:{str(user_id)}, имя:{name}')
#
#     try:
#         if not self.__check_user(str(user_id)):
#             self.logger.debug(f'Пользователь не найден. id пользователя:{str(user_id)}')
#             self.add_user(str(user_id))
#         if not self.check_link(str(user_id), name):
#             self.logger.debug(f'Ссылка не найдена не найдена. id пользователя:{str(user_id)}, имя:{name}')
#             return False
#
#         del self.db[str(str(user_id))][name]
#         self.__dump_db()
#         return True
#     except Exception as e:
#         self.logger.error(f'Не удалось удалить ссылку. id пользователя:{str(user_id)}, имя:{name}', e)
#         return False

# def remove_all(self, str(user_id): int):
#     self.logger.debug(f'Удаление всех ссылок. id пользователя:{str(user_id)}')
#
#     try:
#         if not self.__check_user(str(user_id)):
#             self.logger.debug(f'Пользователь не найден. id пользователя:{str(user_id)}')
#             self.add_user(str(user_id))
#             return True
#
#         self.db[str(str(user_id))] = {}
#         self.__dump_db()
#         return True
#     except Exception as e:
#         self.logger.error(f'Не удалось все ссылки. id пользователя:{str(user_id)}', e)
#         return False
