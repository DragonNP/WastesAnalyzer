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
from io import BytesIO
import matplotlib.pyplot as plt

logger = logging.getLogger('plot_handler')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

GET_YEAR, SEND_PLOT = range(2)


def get():
    return ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Вывести график'), start_send_plot)],
        states={
            GET_YEAR: [MessageHandler(Filters.text, get_year)],
            SEND_PLOT: [MessageHandler(Filters.text, send_plot)],
        },
        fallbacks=[MessageHandler(Filters.text('Назад'), cancel)]
    )


def start_send_plot(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.debug(f'Начало формирования графика. пользователь:{user_id}')

    keyboard = [['Назад']]
    for name in users.get_categories_name(user_id):
        keyboard.append([name])

    update.message.reply_text('Выбери категорию по какой вы хотите сформировать график',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return GET_YEAR


def get_year(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. пользователь:{user_id}, категория:{category}')

    keyboard = [['Назад']]
    for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()]):
        keyboard.append([name])

    update.message.reply_text('Отлично! Теперь введите год за который вы сформировать график',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))
    return SEND_PLOT


def send_plot(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id
    category = context.user_data['category']
    year = update.message.text

    logger.info(f'Отправка графика. пользователь:{user_id} категория:{category} год:{year}')

    datas = users.get_datas(user_id, category)
    months = []
    values = []

    for key in sorted([int(x) for x in datas[year].keys()]):
        months.append(key)
        values.append(int(datas[year][str(key)]))

    context.bot.send_photo(user_id,
                           photo=_generate_plot(months, values),
                           reply_markup=helper.get_user_keyboard())

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление показаний. id пользователя:{user_id}')

    del context.user_data['category']
    del context.user_data['year']
    del context.user_data['month']
    del context.user_data['category']
    return ConversationHandler.END


def _generate_plot(month: list, data: list):
    fig, ax = plt.subplots()

    x = month
    y = data

    plot_file = BytesIO()
    ax.plot(x, y)
    plt.xlabel("Месяц")
    plt.ylabel("Показания")
    fig.savefig(plot_file, format='png')
    plot_file.seek(0)

    return plot_file