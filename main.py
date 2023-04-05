from variables import *
import helper
from databases import users
from handlers import plot_handler, data_handler
import logging
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    Application,
)

logger = logging.getLogger('main')
logger.setLevel(GLOBAL_LOGGER_LEVEL)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# TODO: Выбор типа графика:, 1 год, 2 года или все года
# TODO: Далекое будующие :) Можно выбрать сколько раз записывать расходы: раз в месяц, раз в год, каждый день

async def send_start_msg(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Новое сообщение: /start или /help. пользователь:{user_id}')

    users.add_user(user_id)

    await update.message.reply_text('''Добро пожаловать! Я помогу проанализировать Ваши расходы на коммунальные услуги.

Попробуйте сами:
 ⁃ Нажмите кнопку "Добавить расход"
 ⁃ Укажите категорию для ее добавления
 ⁃ Введите: год, месяц, сумму расхода
При двух и более добавленных расходов, Вы сможете сформировать график, нажав на кнопку "Сформировать график".
Приятного пользования 🤗

Техподдержка:
- Телеграмм t.me/dragon_np
- Почта dragonnp@yandex.ru    
''',
                                    disable_web_page_preview=True,
                                    reply_markup=helper.get_user_keyboard())


async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error: Exception = context.error
    logger.exception(error)
    await update.message.reply_text(
        'Произошла ошибка.\n'
        'Пожалуйста, свяжитесь со мной через телеграм - t.me/dragon_np или почту - dragonnp@yandex.ru',
        disable_web_page_preview=True,
        reply_markup=helper.get_user_keyboard())
    return ConversationHandler.END


def main() -> None:
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        handlers=[
                            logging.FileHandler(PATH_TO_LOG),
                            logging.StreamHandler()
                        ])

    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler('start', send_start_msg))
    application.add_handler(CommandHandler('help', send_start_msg))
    application.add_handler(data_handler.get())
    application.add_handler(plot_handler.get())
    application.add_error_handler(error_callback)

    users.load()

    logger.info('Бот работает')
    application.run_polling()


if __name__ == '__main__':
    main()
