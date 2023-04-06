from variables import GLOBAL_LOGGER_LEVEL, USER_ID_ADMIN, PATH_TO_LOG
import helper
from databases import users, polls, db_messages
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
        entry_points=[MessageHandler(filters.Text([db_messages.DataHandler.data_btn]), start_add_data)],
        states={
            CATEGORY: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), add_category)],
            YEAR: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), add_year)],
            MONTH: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), add_month)],
            DATA: [MessageHandler(filters.TEXT & (~filters.Text([db_messages.cancel_btn])), add_data)],
        },
        fallbacks=[MessageHandler(filters.Text([db_messages.cancel_btn]), cancel)]
    )


async def start_add_data(update: Update, context: CallbackContext) -> int:
    try:
        user_id = update.message.from_user.id

        logger.debug(f'Начало добавления показания. id:{user_id}')

        keyboard = []
        for name in users.get_categories_name(user_id):
            keyboard.append([name])
        if len(keyboard) == 0:
            keyboard = [['Электроэнергия'], ['Водоснабжение'], ['Газ']]
        keyboard.append([db_messages.cancel_btn])

        await update.message.reply_text(db_messages.DataHandler.start,
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))

        polls.update_counter(user_id)
        if polls.check_send_poll(user_id):
            await helper.send_pool(context, user_id)

        return CATEGORY
    except Exception as e:
        return await error(update, e)


async def add_category(update: Update, context: CallbackContext) -> int:
    try:
        user_id = update.message.from_user.id
        context.user_data['category'] = category = update.message.text

        logger.debug(f'Сохраняем категорию. id:{user_id}')

        keyboard = []
        flag = True
        for name in sorted([int(x) for x in users.get_datas(user_id, category).keys()], reverse=True):
            if flag:
                keyboard.append([str(name)])
            else:
                keyboard[-1].append(str(name))
            flag = not flag
        if len(keyboard) == 0:
            keyboard = [['2023', '2022'], ['2021', '2020']]
        keyboard.append([db_messages.cancel_btn])

        await update.message.reply_text(db_messages.DataHandler.add_category,
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))

        polls.update_counter(user_id)
        if polls.check_send_poll(user_id):
            await helper.send_pool(context, user_id)

        return YEAR
    except Exception as e:
        return await error(update, e)


async def add_year(update: Update, context: CallbackContext) -> int:
    try:
        if 'isConvBreak' in context.user_data and context.user_data['isConvBreak']:
            context.user_data['isConvBreak'] = False
            return ConversationHandler.END

        user_id = update.message.from_user.id
        context.user_data['year'] = update.message.text

        logger.debug(f'Сохраняем год. id:{user_id}')

        await update.message.reply_text(
            db_messages.DataHandler.add_year,
            reply_markup=ReplyKeyboardMarkup(helper.get_months_keyboard(), one_time_keyboard=True, resize_keyboard=True))

        polls.update_counter(user_id)
        if polls.check_send_poll(user_id):
            await helper.send_pool(context, user_id)

        return MONTH
    except Exception as e:
        return await error(update, e)


async def add_month(update: Update, context: CallbackContext) -> int:
    try:
        user_id = update.message.from_user.id

        if update.message.text not in helper.get_rus_names_months():
            await update.message.reply_text(db_messages.DataHandler.add_month_error,
                                            reply_markup=ReplyKeyboardMarkup(helper.get_months_keyboard(),
                                                                             one_time_keyboard=True,
                                                                             resize_keyboard=True))
            return MONTH

        context.user_data['month'] = month = helper.get_rus_names_months().index(update.message.text) + 1
        logger.debug(f'Сохраняем месяц. id:{user_id}')

        keyboard = [[db_messages.cancel_btn]]

        await update.message.reply_text(db_messages.DataHandler.add_month,
                                        reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True,
                                                                         resize_keyboard=True))

        polls.update_counter(user_id)
        if polls.check_send_poll(user_id):
            await helper.send_pool(context, user_id)

        return DATA
    except Exception as e:
        return await error(update, e)


async def add_data(update: Update, context: CallbackContext) -> int:
    try:
        user_id = update.message.from_user.id
        data = update.message.text

        logger.debug(f'Сохраняем показания в бд. id:{user_id}')

        users.add_data(user_id,
                       context.user_data['category'],
                       context.user_data['year'],
                       context.user_data['month'],
                       data.replace(',', '.'))

        await update.message.reply_text(db_messages.DataHandler.add_data,
                                        reply_markup=helper.get_user_keyboard())

        polls.update_counter(user_id)
        if polls.check_send_poll(user_id):
            await helper.send_pool(context, user_id)

        return ConversationHandler.END
    except Exception as e:
        return await error(update, e)


async def cancel(update: Update, context: CallbackContext) -> int:
    try:
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
    except Exception as e:
        return await error(update, e)


async def error(update: Update, e: Exception) -> int:
    logger.exception(e)
    await update.message.reply_text(db_messages.error,
                                    disable_web_page_preview=True,
                                    reply_markup=helper.get_user_keyboard())

    if GLOBAL_LOGGER_LEVEL == 'DEBUG':
        await update.get_bot().sendDocument(USER_ID_ADMIN, PATH_TO_LOG)

    return ConversationHandler.END
