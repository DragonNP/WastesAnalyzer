from telegram import ReplyKeyboardMarkup


def get_user_keyboard():
    keyboard = [['Добавить показания'], ['Вывести график']]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)