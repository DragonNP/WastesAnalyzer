from variables import GLOBAL_LOGGER_LEVEL
import helper
from databases import users
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    CallbackContext,
    MessageHandler,
    filters,
)

logger = logging.getLogger('data_handler')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

CATEGORY, YEAR, MONTH, DATA = range(4)


def get():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['Добавить расход']), start_add_data)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), add_category)],
            YEAR: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), add_year)],
            MONTH: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), add_month)],
            DATA: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), add_data)],
        },
        fallbacks=[MessageHandler(filters.Text(['Назад']), cancel)]
    )


async def start_add_data(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.debug(f'Начало добавления показания. id:{user_id}')

    keyboard = []
    for name in users.get_categories_name(user_id):
        keyboard.append([name])
    keyboard.append(['Назад'])

    await update.message.reply_text(
        'Выберите в какую категорию вы хотите добавить расход. Или введите другую, чтобы ее создать',
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CATEGORY


async def add_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. id:{user_id}, категория:{category}')

    keyboard = []
    for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()]):
        keyboard.append([str(name)])
    keyboard.append(['Назад'])

    await update.message.reply_text('Отлично! Теперь введите год за который вы хотите добавить расход',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))

    return YEAR


async def add_year(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['year'] = year = update.message.text

    logger.debug(f'Сохраняем год. id:{user_id}, год:{year}')

    keyboard = []
    names_rus_months = helper.get_rus_names_months()

    flag = True
    for name in names_rus_months:
        if flag:
            keyboard.append([name])
            flag = False
            continue
        keyboard[-1].append(name)
        flag = True
    keyboard.append(['Назад'])

    await update.message.reply_text(
        'Отлично! Теперь введите месяц за который вы хотите добавить расход',
        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return MONTH


async def add_month(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['month'] = month = helper.get_rus_names_months().index(update.message.text) + 1

    logger.debug(f'Сохраняем месяц. id:{user_id}, месяц:{month}')

    keyboard = [['Назад']]

    await update.message.reply_text('Отлично! И последний шаг, введите сам расход',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))

    return DATA


async def add_data(update: Update, context: CallbackContext) -> int:
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
                   data.replace(',', '.'))

    await update.message.reply_text('Супер. Показания переданы',
                                    reply_markup=helper.get_user_keyboard())

    return ConversationHandler.END


async def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление показаний. id пользователя:{user_id}')

    if 'category' in context.user_data:
        del context.user_data['category']
    if 'year' in context.user_data:
        del context.user_data['year']
    if 'month' in context.user_data:
        del context.user_data['month']

    await update.message.reply_text('Хорошо, отменяем.',
                                    reply_markup=helper.get_user_keyboard())
    return ConversationHandler.END
