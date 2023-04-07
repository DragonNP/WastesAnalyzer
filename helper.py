from telegram import ReplyKeyboardMarkup
from telegram.ext import (
    ContextTypes,
)
from databases import db_messages


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


def get_months_keyboard():
    keyboard = []
    names_rus_months = get_rus_names_months()
    flag = True
    for name in names_rus_months:
        if flag:
            keyboard.append([name])
            flag = False
            continue
        keyboard[-1].append(name)
        flag = True
    keyboard.append(['Отменить'])

    return keyboard


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


async def send_pool(context: ContextTypes.DEFAULT_TYPE, user_id: int):
    message = await context.bot.send_poll(
        user_id,
        db_messages.Poll.question,
        db_messages.Poll.options,
        is_anonymous=False,
        allows_multiple_answers=False,
    )
    payload = {
        message.poll.id: {
            "questions": db_messages.Poll.options,
            "message_id": message.message_id,
            "chat_id": user_id,
            "answers": 0,
        }
    }
    context.bot_data.update(payload)


def is_number(s: str):
    for i in s:
        try:
            if i not in [',', '.']:
                int(i)
        except ValueError:
            return False
    return True


def is_year(year: str):
    if is_number(year) and 1970 <= int(year) <= 2023:
        return True
    return False
