
import json
import os
import sys
from http import HTTPStatus
import time
import logging
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
import telegram

from exceptions import NotTwoHundred

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 5
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}
logger = logging.getLogger(__name__)


def send_message(bot, message):
    """Посылаем сообщение в Телеграм."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=f'{message}'
        )
    except telegram.error.TelegramError:
        raise telegram.error.TelegramError('Телеграм не отвечает')


def get_api_answer(current_timestamp):
    """Обращаямся к API Практикума. Возвращаем отклик в формате json."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    try:
        response = requests.get(
            url=ENDPOINT,
            headers=HEADERS,
            params=params
        )
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException('Запрос отклонен.')
    if response.status_code != HTTPStatus.OK:
        raise NotTwoHundred('Ошибка сервера.')
    try:
        return response.json()
    except json.JSONDecodeError:
        raise json.JSONDecodeError('Ошибка json.')


def check_response(response):
    """Проверяем, что приходит список работ и возвращаем его."""
    if not isinstance(response, dict):
        raise TypeError
    if 'homeworks' not in response:
        raise KeyError
    if not isinstance(response['homeworks'], list):
        raise TypeError
    return response['homeworks']


def parse_status(homework):
    """Витаскиваем из запроса имя и статус работы.
    И возвращаем сообщение информирующее нас о изменении статуса.
    """
    try:
        homework_name = homework['homework_name']
        homework_status = homework['status']
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except KeyError:
        raise KeyError('Ошибка ключа')


def check_tokens():
    """Проверяем, что все переменные окружения есть."""
    tokens = (TELEGRAM_TOKEN, PRACTICUM_TOKEN, TELEGRAM_CHAT_ID,)
    return all(tokens)


def main():
    """Основная логика работы бота."""
    if check_tokens() is False:
        sys.exit()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    last_status = ''
    while True:
        try:
            response = get_api_answer(current_timestamp=current_timestamp)
            homework = check_response(response)
            status = homework[0]['status']
            if status != last_status:
                last_status = f'{status}'
                message = parse_status(homework[0])
                send_message(bot, message)
            else:
                logging.debug('Статус не обновился.')
        except Exception as error:
            logging.error(error)
            send_message(error)
        finally:
            time.sleep(RETRY_TIME)


if __name__ == '__main__':
    handler = RotatingFileHandler(
        filename='program.log',
        mode='w',
        maxBytes=50000000,
        backupCount=5,
        encoding='UTF-8'
    )
    handlers = (handler,)
    logging.basicConfig(
        level=logging.DEBUG,
        handlers=handlers,
        format='%(asctime)s, %(levelname)s, %(message)s'
    )
    main()
