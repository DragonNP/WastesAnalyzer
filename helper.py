from telegram import ReplyKeyboardMarkup


def get_user_keyboard():
    keyboard = [['Добавить расход'], ['Сформировать график']]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_rus_names_months():
    return ['Январь',
            'Февраль',
            'Март',
            'Апрель',
            'Май',
            'Июнь',
            'Июль',
            'Август',
            'Сентябрь',
            'Октябрь',
            'Ноябрь',
            'Декабрь']


def get_min_rus_names_months():
    return ['Янв',
            'Фев',
            'Март',
            'Апр',
            'Май',
            'Июнь',
            'Июль',
            'Авг',
            'Сен',
            'Окт',
            'Нояб',
            'Дек']
