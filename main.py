from const_variables import *
import telegram
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import (
    ConversationHandler,
    Updater,
    CommandHandler,
    CallbackContext,
    MessageHandler,
    Filters, CallbackQueryHandler,
)

from database import UsersDB

logger = logging.getLogger('main')
logger.setLevel(GLOBAL_LOGGER_LEVEL)

users = UsersDB()

CATEGORY, YEAR, MONTH, DATA = range(4)


def get_user_keyboard():
    keyboard = [['Добавить показания']]

    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def send_start_msg(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Новое сообщение: /start или /help. пользователь:{user_id}')

    users.add_user(user_id)

    # TODO: Добавить приветственное сообщение
    update.message.reply_text('...'
                              'Техподдержка: телеграм t.me/dragon_np почта: dragonnp@yandex.ru',
                              disable_web_page_preview=True, reply_markup=get_user_keyboard())


def start_add_data(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id

    logger.debug(f'Начало добавления показания. пользователь:{user_id}')

    keyboard = [['Назад']]
    for name in users.get_categories(user_id): keyboard.append([name])

    update.message.reply_text('Выберите в какую категорию вы хотите добавить показания. Или введите другую, чтобы ее '
                              'создать',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return CATEGORY


def add_category(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['category'] = category = update.message.text

    logger.debug(f'Сохраняем категорию. пользователь:{user_id}, категория:{category}')

    keyboard = [['Назад']]

    users.add_category(user_id, category)

    update.message.reply_text('Отлично! Теперь введите год за который вы хотите добавить показания',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return YEAR


def add_year(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['year'] = year = update.message.text

    logger.debug(f'Сохраняем год. пользователь:{user_id}, год:{year}')

    keyboard = [['Назад']]

    update.message.reply_text('Отлично! Теперь введите месяц (в числовом формате) за который вы хотите добавить показания',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return MONTH


def add_month(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    context.user_data['month'] = month = update.message.text

    logger.debug(f'Сохраняем год. пользователь:{user_id}, месяц:{month}')

    keyboard = [['Назад']]

    update.message.reply_text('Отлично! И последний шаг, введите сами показания',
                              reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True))

    return DATA


def add_data(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    data = update.message.text

    logger.debug(f'Сохраняем показания в файл. пользователь:{user_id}, показания:{data}')

    users.add_data(user_id,
                   context.user_data['category'],
                   context.user_data['year'],
                   context.user_data['month'],
                   data)

    update.message.reply_text('Супер. Показания переданы',
                              reply_markup=get_user_keyboard())

    return ConversationHandler.END


def cancel(update: Update, context: CallbackContext) -> int:
    user_id = update.message.from_user.id

    logger.debug(f'Пользователь отменил добавление показаний. id пользователя:{user_id}')

    del context.user_data['category']
    del context.user_data['year']
    del context.user_data['month']
    return ConversationHandler.END


def error_callback(update: Update, context: CallbackContext):
    error: Exception = context.error

    logger.error(error)
    update.message.reply_text(
        'Произошла ошибка. Пожалуйста, свяжитесь со мной через телеграм t.me/dragon_np или через почту dragonnp@yandex.ru')


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create the Updater and pass it your bot token.
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', send_start_msg))
    dispatcher.add_handler(CommandHandler('help', send_start_msg))

    add_data_handler = ConversationHandler(
        entry_points=[MessageHandler(Filters.text('Добавить показания'), start_add_data)],
        states={
            CATEGORY: [MessageHandler(Filters.text, add_category)],
            YEAR: [MessageHandler(Filters.text, add_year)],
            MONTH: [MessageHandler(Filters.text, add_month)],
            DATA: [MessageHandler(Filters.text, add_data)],
        },
        fallbacks=[MessageHandler(Filters.text('Назад'), cancel)]
    )
    dispatcher.add_handler(add_data_handler)

    dispatcher.add_error_handler(error_callback)

    # Start the Bot
    updater.start_polling()

    logger.info('Бот работает')

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
