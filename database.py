import json
from const_variables import *


class UsersDB:
    logger = logging.getLogger('user_db')

    def __init__(self):
        self.db = {}
        self.logger.setLevel(GLOBAL_LOGGER_LEVEL)
        self.logger.debug('Инициализация базы данных пользователей')

        self.location = os.path.expanduser(PATH_TO_USERS_DATA_BASE)
        self.load(self.location)

    def load(self, location):
        self.logger.debug('Загрузка базы данных')

        if os.path.exists(location):
            self.__load()
        return True

    def __load(self):
        self.logger.debug('Загрузка базы данных из файлв')
        self.db = json.load(open(self.location, 'r'))

    def __check_user(self, user_id: int):
        res = str(user_id) in self.db.keys()
        self.logger.debug(f'Проверка пользователе в базе данных. результат:{res}')
        return res

    def __dump_db(self):

        self.logger.debug('Сохранение базы данных в файл')
        try:
            json.dump(self.db, open(self.location, 'w+'))
            return True
        except Exception as e:
            self.logger.error(e)
            return False

    def add_user(self, user_id):
        self.logger.debug(f'Создание пользователя. id пользователя:{user_id}')

        try:
            if self.__check_user(user_id):
                self.logger.debug(f'Пользователь уже создан. id пользователя:{user_id}')
                return False

            self.db[str(user_id)] = {}
            self.__dump_db()
            return True
        except Exception as e:
            self.logger.error(f'Не удалось сохранить пользователя. id пользователя:{user_id}', e)
            return False

    def get_datas(self, user_id: int, category: str):
        self.logger.debug(
            f'Запрос всех показаний пользователя. id пользователя:{user_id} категория:{category}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)

            return self.db[str(user_id)][category]
        except Exception as e:
            self.logger.error(
                f'Не удалось отправить все показания. id пользователя:{user_id} категория:{category}', e)
            return {}

    def get_categories_name(self, user_id: int):
        self.logger.debug(
            f'Запрос категорий пользователя. id пользователя:{user_id}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
                self.add_user(user_id)

            return list(self.db[str(user_id)].keys())
        except Exception as e:
            self.logger.error(
                f'Не удалось категории пользователя. id пользователя:{user_id}', e)
            return {}

    def add_category(self, user_id: int, category_name: str):
        debug_text = f'id пользователя:{user_id}, имя:{category_name}'

        self.logger.debug(f'Добавление категории. {debug_text}')

        try:
            if not self.__check_user(user_id):
                self.logger.debug(f'Пользователь не найден. {debug_text}')
                self.add_user(user_id)

            if category_name in self.db[str(user_id)]:
                self.logger.error(f'Название совпадает с уже добавленной категорией. {debug_text}')
                return False, ''

            self.db[str(user_id)][category_name] = {}
            self.__dump_db()
            return True, ''
        except Exception as e:
            self.logger.error(f'Не удалось сохранить категорию. {debug_text}', e)
            return False, ''

    def add_data(self, user_id: int, category: str, year: str, month: str, data: str):
        user_id = str(user_id)

        debug_text = f'id пользователя:{user_id}, год:{year}, месяц:{month}, данные:{data}'

        self.logger.debug(f'Добавление показания. {debug_text}')

        try:
            if not(category in self.db[user_id]):
                self.logger.error(f'Категория не найдена. Не удалось добавить показания {debug_text}')
                return
            if year not in self.db[user_id][category]:
                self.db[user_id][category][year] = {}
            if month not in self.db[user_id][category][year]:
                self.db[user_id][category][year][month] = data
                self.__dump_db()
            else:
                self.logger.error(f'Показания уже переданы за этот период. Не удалось добавить показания {debug_text}')

            return True, ''
        except Exception as e:
            self.logger.error(f'Категория не найдена. Не удалось добавить показания {debug_text}', e)
            return False, ''

    # def check_link(self, user_id: int, name: str):
    #     res = name in self.db[str(user_id)]
    #     self.logger.debug(f'Проверка ссылки в базе данных. результат:{res}')
    #     return res

    # def remove_link(self, user_id: int, name: str):
    #     self.logger.debug(f'Удаление ссылки. id пользователя:{user_id}, имя:{name}')
    #
    #     try:
    #         if not self.__check_user(user_id):
    #             self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
    #             self.add_user(user_id)
    #         if not self.check_link(user_id, name):
    #             self.logger.debug(f'Ссылка не найдена не найдена. id пользователя:{user_id}, имя:{name}')
    #             return False
    #
    #         del self.db[str(user_id)][name]
    #         self.__dump_db()
    #         return True
    #     except Exception as e:
    #         self.logger.error(f'Не удалось удалить ссылку. id пользователя:{user_id}, имя:{name}', e)
    #         return False

    # def remove_all(self, user_id: int):
    #     self.logger.debug(f'Удаление всех ссылок. id пользователя:{user_id}')
    #
    #     try:
    #         if not self.__check_user(user_id):
    #             self.logger.debug(f'Пользователь не найден. id пользователя:{user_id}')
    #             self.add_user(user_id)
    #             return True
    #
    #         self.db[str(user_id)] = {}
    #         self.__dump_db()
    #         return True
    #     except Exception as e:
    #         self.logger.error(f'Не удалось все ссылки. id пользователя:{user_id}', e)
    #         return False
