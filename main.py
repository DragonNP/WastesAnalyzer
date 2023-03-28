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

# TODO: Добавить вариацию измерений кВт*Ч или литры и так далее
# TODO: Протестировать бота на отказо устойчивость
# TODO: Выбор типа графика:, 1 год, 2 года или все года
# TODO: Далеекое будующие :) Можно выбрать сколько раз записывать расходы: раз в месяц, раз в год, каждый день
# TODO: Мб пересмотреть бота и сделать траты ввиде денег? или оставить специфичные измерения

async def send_start_msg(update: Update, _) -> None:
    user_id = update.message.from_user.id

    logger.info(f'Новое сообщение: /start или /help. пользователь:{user_id}')

    users.add_user(user_id)

    await update.message.reply_text('Привет! Данный бот поможет тебе анализоровать свои расходы на любую категорию.\n'
                                    'Попробуйте сами, нажмите кнопку "Добавить расход" укажите год, месяц, расход.\n'
                                    'При двух и более добавленных расходов, '
                                    'Вы можете сформировать график нажав на кнопку "Сформировать график"\n'
                                    'Приятного использования :)\n'
                                    'Техподдержка: телеграм t.me/dragon_np почта: dragonnp@yandex.ru',
                                    disable_web_page_preview=True,
                                    reply_markup=helper.get_user_keyboard())


async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error: Exception = context.error

    logger.error(error)
    await update.message.reply_text(
        'Произошла ошибка.\n'
        'Пожалуйста, свяжитесь со мной через телеграм t.me/dragon_np или через почту dragonnp@yandex.ru',
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
