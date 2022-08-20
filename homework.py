
import os
import time
import logging
from logging.handlers import RotatingFileHandler

import requests
from dotenv import load_dotenv
import telegram

from exceptions import EmptyList

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

variables = {
    'PRACTICUM_TOKEN': PRACTICUM_TOKEN,
    'TELEGRAM_TOKEN': TELEGRAM_TOKEN,
    'TELEGRAM_CHAT_ID': TELEGRAM_CHAT_ID,
}

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}

logging.basicConfig(
    level=logging.INFO,
    filename='program.log',
)
logger = logging.getLogger(__name__)
handler = RotatingFileHandler(
    filename='program.log',
    mode='w',
    maxBytes=50000000,
    backupCount=5,
    encoding='UTF-8'
)
formatter = logging.Formatter(
    '%(asctime)s, %(levelname)s, %(message)s',
)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)


def send_message(bot, message):
    """Посылаем сообщение в Телеграм."""
    bot.send_message(
        chat_id=TELEGRAM_CHAT_ID,
        text=f'{message}'
    )
    logging.info('Сообщение об изменению статуса отправлено в Телеграм.')


def get_api_answer(current_timestamp):
    """Обращаямся к API Практикума. Возвращаем отклик в формате json."""
    timestamp = current_timestamp or int(time.time())
    params = {'from_date': timestamp}
    response = requests.get(
        url=ENDPOINT,
        headers=HEADERS,
        params=params
    )
    if response.status_code != 200:
        logging.error('Сервер не отвечает.')
        raise Exception
    else:
        return response.json()


def check_response(response):
    """Проверяем, что приходит список работ и возвращаем его."""
    if isinstance(response['homeworks'], list):
        return response['homeworks']
    elif len(response['homeworks']) < 1:
        logging.error('Список пуст')
        raise EmptyList
    else:
        Exception


def parse_status(homework):
    """Витаскиваем из запроса имя и статус работы. И возвращаем сообщение
    информирующее нас о изменении статуса."""
    homework_name = homework['homework_name']
    homework_status = homework['status']
    try:
        verdict = HOMEWORK_STATUSES[homework_status]
        return f'Изменился статус проверки работы "{homework_name}". {verdict}'
    except TypeError as error:
        mess = f'Ошибка {error} в получении информации, Список работ пуст'
        logging.error(mess)
        return mess
    except IndexError:
        pass


def check_tokens():
    """Проверяем, что все переменные окружения есть."""
    if TELEGRAM_TOKEN:
        return True
    if PRACTICUM_TOKEN:
        return True
    if TELEGRAM_CHAT_ID:
        return True
    else:
        mess = 'Ошибка токена. Проверте перепенные окружания'
        logging.critical(mess)
        return False


def main():
    """Основная логика работы бота."""
    check_tokens()
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    current_timestamp = int(time.time())
    statuses = []
    while True:
        if check_tokens() is True:
            try:
                response = get_api_answer(current_timestamp=current_timestamp)
                homework = check_response(response)
                status = homework[0]['status']
                statuses.append(status)
                if len(statuses) > 2:
                    del statuses[0]
                if statuses[0] != statuses[-1]:
                    message = parse_status(homework[0])
                    send_message(bot, message)
                else:
                    logging.debug('Статус не обновился')
                time.sleep(RETRY_TIME)
            except Exception as error:
                statuses.append(error)
                if len(statuses) > 2:
                    del statuses[0]
                logging.error(error)
                time.sleep(RETRY_TIME)
            else:
                pass
        else:
            break


if __name__ == '__main__':
    main()
