from variables import *
import helper
from databases import users, polls
from handlers import plot_handler, data_handler
import logging
from telegram import Update
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    ContextTypes,
    Application,
    PollAnswerHandler,
)

logger = logging.getLogger('main')
logger.setLevel(GLOBAL_LOGGER_LEVEL)
log_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')


# TODO: Выбор типа графика:, 1 год, 2 года или все года
# TODO: Далекое будующие :) Можно выбрать сколько раз записывать расходы: раз в месяц, раз в год, каждый день

async def send_start_msg(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
    polls.update_counter(user_id)
    if polls.check_send_poll(user_id):
        await helper.send_pool(context, user_id)


async def receive_poll_answer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    poll_answer = update.poll_answer
    answered_poll = context.bot_data[poll_answer.poll_id]
    user_answer = answered_poll["questions"][poll_answer.option_ids[0]]

    if user_answer == 'Есть предложения':
        await context.bot.send_message(answered_poll["chat_id"],
                                       "Рад что у Вас есть предложения по улучшению бота!\n"
                                       "Написать все свои пожелания можете тут: @dragon_np или отправить их на почту: dragonnp@yandex.ru")
    polls.save_result(user_answer)

    await context.bot.send_message(answered_poll["chat_id"], "Спасибо! Ты делаешь бота еще лучше)")
    await context.bot.stop_poll(answered_poll["chat_id"], answered_poll["message_id"])


async def error_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    error: Exception = context.error
    logger.exception(error)
    await update.message.reply_text(
        'Произошла ошибка.\n'
        'Пожалуйста, свяжитесь со мной через телеграм - t.me/dragon_np или почту - dragonnp@yandex.ru',
        disable_web_page_preview=True,
        reply_markup=helper.get_user_keyboard())

    if GLOBAL_LOGGER_LEVEL == 'DEBUG':
        await update.get_bot().sendDocument(USER_ID_ADMIN, PATH_TO_LOG)

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
    application.add_handler(PollAnswerHandler(receive_poll_answer))
    application.add_error_handler(error_callback)

    users.load()
    polls.load()

    logger.info('Бот работает')
    application.run_polling()


if __name__ == '__main__':
    main()
