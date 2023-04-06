from variables import GLOBAL_LOGGER_LEVEL
import helper
from databases import users, polls, db_messages
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
        entry_points=[MessageHandler(filters.Text([db_messages.PlotHandler.plot_btn]), start)],
        states={
            GET_YEAR: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), get_year)],
            SEND_PLOT: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), send_plot)],
        },
        fallbacks=[MessageHandler(filters.Text([db_messages.cancel_btn]), cancel)],

    )


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Начало формирования графика. id:{user_id}')

    keyboard = []
    for name in users.get_categories_name(user_id):
        keyboard.append([name])
    keyboard.append([db_messages.cancel_btn])

    if len(keyboard) == 1:
        await update.message.reply_text(db_messages.PlotHandler.start_error,
                                        reply_markup=helper.get_user_keyboard())
        return ConversationHandler.END

    await update.message.reply_text(db_messages.PlotHandler.start,
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))

    polls.update_counter(user_id)
    if polls.check_send_poll(user_id):
        await helper.send_pool(context, user_id)

    return GET_YEAR


async def get_year(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. id:{user_id}')

    if not users.check_category(user_id, category):
        keyboard = []
        for name in users.get_categories_name(user_id):
            keyboard.append([name])
        keyboard.append([db_messages.cancel_btn])

        await update.message.reply_text(db_messages.PlotHandler.category_error,
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))
        return GET_YEAR

    keyboard = []
    flag = True
    for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()], reverse=True):
        if flag:
            keyboard.append([str(name)])
        else:
            keyboard[-1].append(str(name))
        flag = not flag
    keyboard.append([db_messages.cancel_btn])

    if len(keyboard) == 1:
        await update.message.reply_text(db_messages.PlotHandler.start_error,
                                        reply_markup=helper.get_user_keyboard())
        return ConversationHandler.END

    await update.message.reply_text(db_messages.PlotHandler.get_year,
                                    reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                     resize_keyboard=True))

    polls.update_counter(user_id)
    if polls.check_send_poll(user_id):
        await helper.send_pool(context, user_id)

    return SEND_PLOT


async def send_plot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id
    category = context.user_data['category']
    year = update.message.text

    if not users.check_year(user_id, category, year):
        keyboard = []
        flag = True
        for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()], reverse=True):
            if flag:
                keyboard.append([str(name)])
            else:
                keyboard[-1].append(str(name))
            flag = not flag
        keyboard.append([db_messages.cancel_btn])

        await update.message.reply_text(db_messages.PlotHandler.year_error,
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))
        return SEND_PLOT

    logger.info(f'Отправка графика. id:{user_id}')

    datas_for_year = users.get_datas(user_id, category)[year]
    title = f'{category}. {year} год.'
    months = []
    values = []

    if len(datas_for_year) < 2:
        await update.message.reply_text(db_messages.PlotHandler.send_plot_error,
                                        reply_markup=helper.get_user_keyboard())
        return ConversationHandler.END

    rus_names_months = helper.get_min_rus_names_months()
    for key in sorted([int(x) for x in datas_for_year.keys()]):
        months.append(rus_names_months[key - 1])
        values.append(float(datas_for_year[str(key)].replace(',', '.')))

    await context.bot.send_photo(user_id,
                                 photo=_generate_plot(title, months, values),
                                 reply_markup=helper.get_user_keyboard())

    polls.update_counter(user_id)
    if polls.check_send_poll(user_id):
        await helper.send_pool(context, user_id)

    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление показаний. id:{user_id}')

    if 'category' in context.user_data:
        del context.user_data['category']
    if 'year' in context.user_data:
        del context.user_data['year']
    if 'month' in context.user_data:
        del context.user_data['month']

    await update.message.reply_text(db_messages.cancel_msg,
                                    reply_markup=helper.get_user_keyboard())

    polls.update_counter(user_id)
    if polls.check_send_poll(user_id):
        await helper.send_pool(context, user_id)

    return ConversationHandler.END


def _generate_plot(title, x: list, y: list):
    fig, ax = plt.subplots()

    plot_file = BytesIO()
    ax.plot(x, y)

    fig.autofmt_xdate()
    plt.title(title)
    plt.xlabel(db_messages.PlotHandler.x_label)
    plt.ylabel(db_messages.PlotHandler.y_label)
    plt.autoscale()

    fig.savefig(plot_file, format='png')
    plot_file.seek(0)
    return plot_file
