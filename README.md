# homework_bot
## Описание:
Телеграм-бот, регулярно делает запрос к API учебной платформы Яндекс Практикум с целью, получить статус выполненой домашней работы.
Если статус работы изменился, бот присылает сообщение с результатами запроса, в телеграм.

##Развертывание:
Клонировать проект:
<code>https://github.com/kultmet/homework_bot.git</code>

Переходим в папку проекта, устанавливаем и активируем виртуальное окружение:
<code>cd [путь к папке проекта]
python -m venv venv
source venv/Scripts/activate
</code>

Включаем бота:
<code>python homework.py</code>

Требования:
<code>
flake8==3.9.2
flake8-docstrings==1.6.0
pytest==6.2.5
python-dotenv==0.19.0
python-telegram-bot==13.7
requests==2.26.0
</code>

Основной рабочий инструмент - python telegram bot

Проект сейчас крутится на сервере Heroku.

Планов по доработке нет.
