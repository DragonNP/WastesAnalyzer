from variables import *
import helper
from databases import users
from handlers import plot_handler, data_handler
import logging
from telegram import Update
from telegram.ext import (
    Updater,
    CommandHandler,
    CallbackContext,
)

logger = logging.getLogger('main')
logger.setLevel(GLOBAL_LOGGER_LEVEL)


def send_start_msg(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Новое сообщение: /start или /help. пользователь:{user_id}')

    users.add_user(user_id)

    # TODO: Добавить приветственное сообщение
    update.message.reply_text('...'
                              'Техподдержка: телеграм t.me/dragon_np почта: dragonnp@yandex.ru',
                              disable_web_page_preview=True,
                              reply_markup=helper.get_user_keyboard())


def error_callback(update: Update, context: CallbackContext):
    error: Exception = context.error

    logger.error(error)
    update.message.reply_text(
        'Произошла ошибка. Пожалуйста, свяжитесь со мной через телеграм t.me/dragon_np или через почту dragonnp@yandex.ru',
        reply_markup=helper.get_user_keyboard())


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Create the Updater and pass it your bot token.
    updater = Updater(token=TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', send_start_msg))
    dispatcher.add_handler(CommandHandler('help', send_start_msg))

    dispatcher.add_handler(data_handler.get())
    dispatcher.add_handler(plot_handler.get())

    dispatcher.add_error_handler(error_callback)

    users.load()

    # Start the Bot
    updater.start_polling()

    logger.info('Бот работает')

    # Run the bot until the user presses Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT
    updater.idle()


if __name__ == '__main__':
    main()
