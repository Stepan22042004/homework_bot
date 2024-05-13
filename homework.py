import os
import time
import logging
from http import HTTPStatus

from dotenv import load_dotenv
import requests
from telebot import TeleBot

import exceptions

load_dotenv()


PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens() -> bool:
    """есть ли токены в переменных окружения."""
    no_token = ''

    if PRACTICUM_TOKEN is None:
        no_token += 'PRACTICUM_TOKEN '
    if TELEGRAM_TOKEN is None:
        no_token += 'TELEGRAM_TOKEN '
    if TELEGRAM_CHAT_ID is None:
        no_token += 'TELEGRAM_CHAT_ID'
    if no_token == '':
        return True
    else:
        logging.critical(no_token)
        raise exceptions.NoTokensException()


def send_message(bot: TeleBot, message: str) -> bool:
    """Отправляет сообщение о статусе ревью."""
    try:
        bot.send_message(TELEGRAM_CHAT_ID, message)
    except Exception:
        logging.exception('message_error')
        return False
    else:
        logging.debug('message_success')
        return True


def get_api_answer(timestamp: time) -> dict:
    """Запрос к api."""
    try:
        homework_statuses = requests.get(
            ENDPOINT,
            headers=HEADERS,
            params=timestamp
        )
        if homework_statuses.status_code != HTTPStatus.OK:
            raise exceptions.GetApiException()
        return homework_statuses.json()
    except requests.RequestException:
        logging.error('endpoint_error')


def check_response(response: dict):
    """Проверка ответа API."""
    if not isinstance(response, dict):
        raise TypeError()
    if 'homeworks' not in response:
        raise exceptions.NoKeyHmwrkException()
    if not isinstance(response['homeworks'], list):
        raise TypeError()
    if len(response['homeworks']) == 0:
        logging.debug('no homework')


def parse_status(homework: dict) -> str:
    """Извлекает информацию о конкретной работе."""
    if 'homework_name' not in homework:
        raise exceptions.NoKeyHmwrkNameException()
    if ('status' not in homework.keys()
            or homework['status'] not in HOMEWORK_VERDICTS):
        raise exceptions.StatusException()

    return (f'Изменился статус проверки работы "{homework["homework_name"]}"'
            f'. {HOMEWORK_VERDICTS[homework["status"]]}')


def main():
    """Main для бота."""
    check_tokens()
    bot = TeleBot(token=TELEGRAM_TOKEN)
    timestamp = int(time.time())
    status = None
    while True:
        try:
            response = get_api_answer({'from_date': timestamp})
            check_response(response)
            new_status = parse_status(response['homeworks'][0])
            if new_status != status:
                send_message(bot, new_status)
                status = new_status
        except exceptions.NoTokensException:
            break
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            send_message(bot, message)

        time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        filemode='w'
    )
    main()
