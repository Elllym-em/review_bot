import logging
import os
import sys
import time
from http import HTTPStatus

import requests
import telegram
from dotenv import load_dotenv

from exceptions import HttpStatusError, NotApiResponse
from exceptions import RequestApiError, SendMessageError

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

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
    return all([
        PRACTICUM_TOKEN,
        TELEGRAM_TOKEN,
        TELEGRAM_CHAT_ID
    ])


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
        )
        logger.debug('Сообщение успешно отправлено.')
    except telegram.error.TelegramError:
        message = 'Сбой при отправке сообщения в Telegram.'
        logger.error(message)
        raise SendMessageError(message)


def get_api_answer(timestamp):
    """Запрос и получение ответа API в формате типа данных Python."""
    payload = {'from_date': timestamp}
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=payload,
        )
    except requests.RequestException as error:
        raise RequestApiError(
            f'Ошибка при запросе к эндпоинту c параметрами {payload}: {error}')

    if homework_statuses.status_code != HTTPStatus.OK:
        raise HttpStatusError(
            f'При запросе к эндпоинту с параметрами {payload} '
            f'получен неверный статус-код ответа: '
            f'статус {homework_statuses.status_code}.')

    return homework_statuses.json()


def check_response(response):
    """Проверка ответа API на соответствие документации."""
    if not response:
        raise NotApiResponse('Ответ API не получен.')
    if not isinstance(response, dict):
        raise TypeError('Полученный ответ API не является словарем.')
    homework = response.get('homeworks')
    if 'current_date' not in response:
        raise KeyError(
            'В полученном ответе API отсутствует ключ "current_date"')
    if not isinstance(homework, list):
        raise TypeError('В полученном ответе API отсутствует список работ.')
    return homework


def parse_status(homework):
    """Извлечение актуального статуса домашней работы."""
    homework_name = homework.get('homework_name')
    if 'homework_name' not in homework:
        raise KeyError('Ключ homework_name не найден в ответе API.')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise KeyError(
            f'В ответе получен неожиданный статус: "{homework_status}".')
    verdict = HOMEWORK_VERDICTS[homework_status]
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
    last_message_error = ''

    while True:
        try:
            response = get_api_answer(timestamp)
            homework = check_response(response)
            if not homework:
                message = 'Пока нет новых статусов.'
                logger.debug('В ответе API отсутствуют новые статусы.')
            else:
                message = parse_status(homework[0])
                if message != last_message:
                    send_message(bot, message)
                    last_message = message
                    timestamp = response.get('current_date')
        except Exception as error:
            message_error = f'Сбой в работе программы: {error}'
            logger.error(message_error, exc_info=True)
            if message_error != last_message_error:
                try:
                    send_message(bot, message_error)
                except SendMessageError:
                    pass
                else:
                    last_message_error = message_error
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.INFO,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(message)s,'
               '%(name)s, %(funcName)s, %(lineno)s'
    )

    main()
