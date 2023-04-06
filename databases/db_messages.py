start_msg = '''Добро пожаловать! Я помогу проанализировать Ваши расходы на коммунальные услуги.

Попробуйте сами:
 ⁃ Нажмите кнопку "Добавить расход"
 ⁃ Укажите категорию для ее добавления
 ⁃ Введите: год, месяц, сумму расхода
При двух и более добавленных расходов, Вы сможете сформировать график, нажав на кнопку "Сформировать график".
Приятного пользования 🤗

Техподдержка:
- Телеграмм t.me/dragon_np
- Почта dragonnp@yandex.ru    
'''
error = 'Произошла ошибка.\n'
'Пожалуйста, свяжитесь со мной через телеграм - t.me/dragon_np или почту - dragonnp@yandex.ru'
cancel_btn = 'Отменить'
cancel_msg = 'Хорошо, отменяем'


class DataHandler:
    data_btn = 'Добавить расход'
    start = 'Выберите введённую ранее категорию или напишите название новой'
    add_category = 'Отлично! Теперь введите год за который вы хотите добавить расход'
    add_year = 'Отлично! Теперь введите месяц за который вы хотите добавить расход'
    add_month_error = 'Такого месяца не существует, введите еще раз'
    add_month = 'Отлично! И последний шаг, введите потраченную сумму'
    add_data = 'Супер. Данные для анализа добавлены'


class PlotHandler:
    plot_btn = 'Сформировать график'
    start = 'Выберите нужную категорию'
    get_year = 'А теперь выберите год'
    send_plot_error = 'За этот Вы указали меньше двух месяцев расходов по этой катерогии.'
    '\nВведите еще расходы за месяца, чтобы построить график.'

    x_label = 'Месяц'
    y_label = 'Сумма, руб.'


class Poll:
    question = 'Вам нравится бот или есть какие-то предложения?'
    options = ['Да', 'Нет', 'Есть предложения']
    any_suggestions = 'Рад что у Вас есть предложения по улучшению бота!\n'
    'Написать все свои пожелания можете тут: @dragon_np или отправить их на почту: dragonnp@yandex.ru'
    no = 'Пожалуйста, расскажите что вам нехватает?\n' \
         'Написать сообщение можете тут: @dragon_np или отправить их на почту: dragonnp@yandex.ru'
    thank = 'Спасибо! Ты делаешь бота еще лучше)'
