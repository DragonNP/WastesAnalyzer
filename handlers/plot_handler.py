from variables import GLOBAL_LOGGER_LEVEL
import helper
from databases import users
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    MessageHandler,
    filters, ContextTypes,
)
from io import BytesIO
import matplotlib.pyplot as plt

logger = logging.getLogger('plot_handler')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

GET_YEAR, SEND_PLOT = range(2)


def get():
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Text(['Сформировать график']), start_send_plot)],
        states={
            GET_YEAR: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), get_year)],
            SEND_PLOT: [MessageHandler(filters.TEXT & (~filters.Text(['Назад'])), send_plot)],
        },
        fallbacks=[MessageHandler(filters.Text(['Назад']), cancel)]
    )


async def start_send_plot(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.debug(f'Начало формирования графика. пользователь:{user_id}')

    keyboard = [['Назад']]
    for name in users.get_categories_name(user_id):
        keyboard.append([name])

    await update.message.reply_text('Выбери категорию по какой вы хотите сформировать график',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return GET_YEAR


async def get_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. пользователь:{user_id}, категория:{category}')

    keyboard = [['Назад']]
    for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()]):
        keyboard.append([str(name)])

    await update.message.reply_text('Отлично! Теперь введите год за который вы сформировать график',
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))
    return SEND_PLOT


async def send_plot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    category = context.user_data['category']
    year = update.message.text

    logger.info(f'Отправка графика. пользователь:{user_id} категория:{category} год:{year}')

    datas_for_year = users.get_datas(user_id, category)[year]
    title = f'{category}. {year} год.'
    months = []
    values = []

    if len(datas_for_year) < 2:
        await update.message.reply_text('За этот Вы указали меньше двух месяцев расходов по этой катерогии.'
                                        '\nВведите еще расходы за месяца, чтобы построить график.',
                                        reply_markup=helper.get_user_keyboard())
        return ConversationHandler.END

    rus_names_months = helper.get_min_rus_names_months()
    for key in sorted([int(x) for x in datas_for_year.keys()]):
        months.append(rus_names_months[key - 1])
        values.append(float(datas_for_year[str(key)].replace(',', '.')))

    await context.bot.send_photo(user_id,
                                 photo=_generate_plot(title, months, values),
                                 reply_markup=helper.get_user_keyboard())

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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


def _generate_plot(title, x: list, y: list):
    fig, ax = plt.subplots()

    plot_file = BytesIO()
    ax.plot(x, y)

    fig.autofmt_xdate()
    plt.title(title)
    plt.xlabel("Месяц")
    plt.ylabel("Показания")
    plt.autoscale()

    fig.savefig(plot_file, format='png')
    plot_file.seek(0)
    return plot_file
