import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import HttpStatusError, NotApiResponse

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.INFO,
    filename='main.log',
    format='%(asctime)s, %(levelname)s, %(message)s,'
           '%(name)s, %(funcName)s, %(lineno)s'
)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(levelname)s - %(message)s - '
    ' %(name)s - %(funcName)s - %(lineno)s'
)
handler = logging.StreamHandler(stream=sys.stdout)
handler.setFormatter(formatter)
logger.addHandler(handler)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Получение переменных окружения."""
    tokens = [
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ]
    if all(tokens):
        return True
    return False


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logger.debug('Сообщение успешно отправлено.')
    except telegram.error.TelegramError:
        logger.error('Сбой при отправке сообщения в Telegram.')


def get_api_answer(timestamp):
    """Запрос и получение ответа API в формате типа данных Python."""
    timestamp = timestamp
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload,
        )
    except Exception as error:
        logger.error(f'Ошибка при запросе к эндпоинту: {error}')

    if homework_statuses.status_code != HTTPStatus.OK:
        logger.error('Получен неверный статус-код ответа.')
        raise HttpStatusError

    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not response:
        logger.error('Ответ API не получен.')
        raise NotApiResponse
    if not isinstance(response, dict):
        message = 'Ответ API не соответствует документации.'
        logger.error(message)
        raise TypeError(message)
    homework = response.get('homeworks')
    if not isinstance(homework, list):
        message = 'Ответ API не соответствует документации.'
        logger.error(message)
        raise TypeError(message)
    if 'homeworks' not in response:
        message = 'В ответе API нет нужных ключей.'
        logger.error(message)
        raise KeyError(message)
    return response.get('homeworks')[0]


def parse_status(homework):
    """Извлечение актуального статуса домашней работы."""
    try:
        homework_name = homework.get('homework_name')
        if 'homework_name' not in homework:
            message = 'Ключ homework_name не найден в ответе API.'
            logger.error(message)
            raise KeyError(message)
        homework_status = homework.get('status')
        verdict = HOMEWORK_VERDICTS[homework_status]
    except KeyError:
        logger.error('В ответе получен неожинданный статус.')

    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    logger.debug('Проверка наличия переменных окружения.')
    if not check_tokens():
        logger.critical('Отсутствует обязательные переменные окружения!')
        exit()

    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    last_message = ''
    last_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if not homework:
                message = 'Пока нет новых статусов.'
                logger.debug('В ответе API отсутствуют новые статусы.')
            else:
                message = parse_status(homework)
                if message != last_message:
                    send_message(bot, message)
                    logger.debug('Сообщение успешно отправлено.')
        except Exception as error:
            if error != last_error:
                message = f'Сбой в работе программы: {error}'
            else:
                message = 'Сообщение об ошибке уже отправлено'
            logger.error(message)
            send_message(bot, message)
            logger.debug('Сообщение успешно отправлено.')
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
