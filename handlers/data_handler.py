from variables import GLOBAL_LOGGER_LEVEL
import helper
from databases import users
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    Filters,
)

logger = logging.getLogger('data_handler')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

CATEGORY, YEAR, MONTH, DATA = range(4)


def get():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Добавить показания'), start_add_data)],
        states={
            CATEGORY: [MessageHandler(Filters.text & (~Filters.text('Назад')), add_category)],
            YEAR: [MessageHandler(Filters.text & (~Filters.text('Назад')), add_year)],
            MONTH: [MessageHandler(Filters.text & (~Filters.text('Назад')), add_month)],
            DATA: [MessageHandler(Filters.text & (~Filters.text('Назад')), add_data)],
        },
        fallbacks=[MessageHandler(Filters.text('Назад'), cancel)]
    )


def start_add_data(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    logger.debug(f'Начало добавления показания. id:{user_id}')

    keyboard = [['Назад']]
    for name in users.get_categories_name(user_id): keyboard.append([name])

    update.message.reply_text(
        'Выберите в какую категорию вы хотите добавить показания. Или введите другую, чтобы ее '
        'создать',
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CATEGORY


def add_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. id:{user_id}, категория:{category}')

    keyboard = [['Назад']]
    for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()]):
        keyboard.append([name])

    update.message.reply_text('Отлично! Теперь введите год за который вы хотите добавить показания',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))

    return YEAR


def add_year(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['year'] = year = update.message.text

    logger.debug(f'Сохраняем год. id:{user_id}, год:{year}')

    keyboard = [['Назад']]

    datas = users.get_datas(user_id, context.user_data['category'])

    if datas != {} and year in datas:
        for name in sorted([int(x) for x in datas[year].keys()]):
            keyboard.append([name])

    update.message.reply_text(
        'Отлично! Теперь введите месяц (в числовом формате) за который вы хотите добавить показания',
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return MONTH


def add_month(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['month'] = month = update.message.text

    logger.debug(f'Сохраняем месяц. id:{user_id}, месяц:{month}')

    keyboard = [['Назад']]

    update.message.reply_text('Отлично! И последний шаг, введите сами показания',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                               resize_keyboard=True))

    return DATA


def add_data(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    data = update.message.text

    logger.debug(f'Сохраняем показания в файл.'
                 f' id:{user_id},'
                 f' категория:{context.user_data["category"]},'
                 f' год:{context.user_data["year"]},'
                 f' месяц:{context.user_data["month"]},'
                 f' показания:{data}')

    users.add_data(user_id,
                   context.user_data['category'],
                   context.user_data['year'],
                   context.user_data['month'],
                   data)

    update.message.reply_text('Супер. Показания переданы',
                              reply_markup=helper.get_user_keyboard())

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление показаний. id пользователя:{user_id}')

    if 'category' in context.user_data:
        del context.user_data['category']
    if 'year' in context.user_data:
        del context.user_data['year']
    if 'month' in context.user_data:
        del context.user_data['month']

    update.message.reply_text('Хорошо, отменяем.',
                              reply_markup=helper.get_user_keyboard())
    return ConversationHandler.END
